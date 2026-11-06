import { resilientStorage } from './offlineManager';
import { apiClient, ApiError } from '../api/client';

export type SyncStatus =
  | 'PENDING'
  | 'SYNCED'
  | 'FAILED_RETRYABLE'
  | 'CONFLICT_ACTION_REQUIRED'
  | 'BLOCKED_BY_DEPENDENCY'
  | 'DISCARDED';

export type AuditEventType =
  | 'TRANSACTION_CREATED'
  | 'SYNC_ATTEMPTED'
  | 'SYNC_SUCCEEDED'
  | 'RETRY_SCHEDULED'
  | 'CONFLICT_DETECTED'
  | 'CONFLICT_PAYLOAD_UPDATED'
  | 'DEPENDENCY_BLOCKED'
  | 'DEPENDENCY_RESOLVED'
  | 'TRANSACTION_DISCARDED';

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  event: AuditEventType;
  details: string;
  metadata?: Record<string, any>;
}

export interface SyncTransaction<T = Record<string, any>> {
  id: string;
  entityType: 'employee' | 'dining_scan' | string;
  tempEntityId: string;
  permanentEntityId?: string;
  parentTempEntityId?: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  endpoint: string;
  httpMethod: 'POST' | 'PUT' | 'DELETE';
  payload: T;
  status: SyncStatus;
  attempts: number;
  maxAttempts: number;
  lastAttemptAt?: string;
  lastError?: {
    message: string;
    status?: number;
    details?: any;
  };
  createdAt: string;
  updatedAt: string;
  auditTrail: AuditLogEntry[];
}

const STORAGE_KEY = '@workforce_sync_ledger_v1';
const MAX_DEFAULT_ATTEMPTS = 5;
const MAX_ARCHIVED_TRANSACTIONS = 50; // Storage pruning threshold for scalability

function createUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

class SyncLedgerManager {
  private transactions: Map<string, SyncTransaction> = new Map();
  private isProcessing = false;
  private listeners: Set<() => void> = new Set();
  private isHydrated = false;

  constructor() {
    this.hydrate();
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    for (const listener of this.listeners) {
      try {
        listener();
      } catch (err) {
        console.error('Error executing SyncLedger listener:', err);
      }
    }
  }

  public async hydrate(): Promise<void> {
    if (this.isHydrated) return;
    try {
      const serialized = await resilientStorage.getItem(STORAGE_KEY);
      if (serialized) {
        const parsed: SyncTransaction[] = JSON.parse(serialized);
        this.transactions.clear();
        for (const tx of parsed) {
          this.transactions.set(tx.id, tx);
        }
      }
      this.isHydrated = true;
      this.notify();
    } catch (err) {
      console.warn('Failed to hydrate sync ledger from storage:', err);
      this.isHydrated = true;
    }
  }

  private async persist(): Promise<void> {
    try {
      const data = Array.from(this.transactions.values());
      await resilientStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (err) {
      console.error('Failed to persist sync ledger:', err);
    }
  }

  private appendAudit(tx: SyncTransaction, event: AuditEventType, details: string, metadata?: Record<string, any>): void {
    const entry: AuditLogEntry = {
      id: createUUID(),
      timestamp: new Date().toISOString(),
      event,
      details,
      metadata,
    };
    tx.auditTrail.push(entry);
    tx.updatedAt = entry.timestamp;
  }

  /**
   * Enqueue a new mutation into the outbox ledger.
   * If it has a parent dependency that is in conflict or blocked, it immediately marks it as BLOCKED_BY_DEPENDENCY.
   */
  public async enqueue<T extends Record<string, any>>(params: {
    entityType: string;
    tempEntityId: string;
    parentTempEntityId?: string;
    action: 'CREATE' | 'UPDATE' | 'DELETE';
    endpoint: string;
    httpMethod: 'POST' | 'PUT' | 'DELETE';
    payload: T;
    maxAttempts?: number;
    autoProcess?: boolean;
  }): Promise<SyncTransaction<T>> {
    await this.hydrate();

    const now = new Date().toISOString();
    const id = createUUID();

    let initialStatus: SyncStatus = 'PENDING';
    const parent = params.parentTempEntityId ? this.getByTempId(params.parentTempEntityId) : null;

    if (parent && (parent.status === 'CONFLICT_ACTION_REQUIRED' || parent.status === 'BLOCKED_BY_DEPENDENCY')) {
      initialStatus = 'BLOCKED_BY_DEPENDENCY';
    }

    const tx: SyncTransaction<T> = {
      id,
      entityType: params.entityType,
      tempEntityId: params.tempEntityId,
      parentTempEntityId: params.parentTempEntityId,
      action: params.action,
      endpoint: params.endpoint,
      httpMethod: params.httpMethod,
      payload: params.payload,
      status: initialStatus,
      attempts: 0,
      maxAttempts: params.maxAttempts || MAX_DEFAULT_ATTEMPTS,
      createdAt: now,
      updatedAt: now,
      auditTrail: [],
    };

    this.appendAudit(
      tx,
      'TRANSACTION_CREATED',
      `Transacción registrada para ${params.entityType} (${params.action}) con ID provisional ${params.tempEntityId}`,
      { initialStatus, parentTempEntityId: params.parentTempEntityId }
    );

    if (initialStatus === 'BLOCKED_BY_DEPENDENCY') {
      this.appendAudit(
        tx,
        'DEPENDENCY_BLOCKED',
        `Pausada automáticamente: la entidad padre (${params.parentTempEntityId}) está en estado de conflicto.`,
        { parentId: parent?.id }
      );
    }

    this.transactions.set(id, tx);
    await this.persist();
    this.notify();

    if (params.autoProcess !== false && initialStatus === 'PENDING') {
      this.processQueue().catch(() => {});
    }

    return tx;
  }

  public getAllTransactions(): SyncTransaction[] {
    return Array.from(this.transactions.values()).sort(
      (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    );
  }

  public getByTempId(tempId: string): SyncTransaction | undefined {
    for (const tx of this.transactions.values()) {
      if (tx.tempEntityId === tempId) return tx;
    }
    return undefined;
  }

  public getById(id: string): SyncTransaction | undefined {
    return this.transactions.get(id);
  }

  /**
   * Updates an existing conflicting draft with new payload values and re-enqueues it for sync.
   */
  public async resolveConflict<T extends Record<string, any>>(
    transactionId: string,
    updatedPayload: Partial<T>
  ): Promise<SyncTransaction | undefined> {
    const tx = this.transactions.get(transactionId);
    if (!tx) return undefined;

    tx.payload = { ...tx.payload, ...updatedPayload };
    tx.status = 'PENDING';
    tx.lastError = undefined;

    this.appendAudit(
      tx,
      'CONFLICT_PAYLOAD_UPDATED',
      'El usuario corrigió los datos en conflicto. Transacción devuelta a la cola de sincronización.',
      { updatedFields: Object.keys(updatedPayload) }
    );

    await this.persist();
    this.notify();

    this.processQueue().catch(() => {});
    return tx;
  }

  /**
   * Explicit rollback/discard requested by the user.
   * Cascades the discard to any children blocked by this parent transaction.
   */
  public async discardTransaction(transactionId: string, reason = 'Descarte manual por el usuario'): Promise<void> {
    const tx = this.transactions.get(transactionId);
    if (!tx) return;

    tx.status = 'DISCARDED';
    this.appendAudit(tx, 'TRANSACTION_DISCARDED', `Transacción descartada: ${reason}`);

    // Cascade to children
    for (const child of this.transactions.values()) {
      if (child.parentTempEntityId === tx.tempEntityId && child.status !== 'SYNCED' && child.status !== 'DISCARDED') {
        child.status = 'DISCARDED';
        this.appendAudit(
          child,
          'TRANSACTION_DISCARDED',
          `Descartada en cascada porque la entidad padre (${tx.tempEntityId}) fue descartada.`
        );
      }
    }

    await this.persist();
    this.notify();
  }

  /**
   * Next actionable transaction in FIFO and causal order that is not blocked.
   */
  private getNextActionableTransaction(): SyncTransaction | null {
    const list = this.getAllTransactions();
    for (const tx of list) {
      if (tx.status === 'PENDING' || tx.status === 'FAILED_RETRYABLE') {
        return tx;
      }
    }
    return null;
  }

  /**
   * Enterprise Drain Loop: Processes pending transactions iteratively.
   * Prevents race conditions when new transactions are enqueued during an active cycle.
   */
  public async processQueue(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;

    try {
      await this.hydrate();

      const processedInThisCycle = new Set<string>();

      while (true) {
        const tx = this.getNextActionableTransaction();
        if (!tx || processedInThisCycle.has(tx.id)) {
          break;
        }

        // Check parent dependency
        if (tx.parentTempEntityId) {
          const parent = this.getByTempId(tx.parentTempEntityId);

          if (parent) {
            if (parent.status === 'CONFLICT_ACTION_REQUIRED' || parent.status === 'BLOCKED_BY_DEPENDENCY') {
              tx.status = 'BLOCKED_BY_DEPENDENCY';
              this.appendAudit(
                tx,
                'DEPENDENCY_BLOCKED',
                `Bloqueada: la entidad padre (${parent.tempEntityId}) requiere resolución de conflicto.`
              );
              await this.persist();
              this.notify();
              processedInThisCycle.add(tx.id);
              continue;
            }

            if (parent.status === 'PENDING' || parent.status === 'FAILED_RETRYABLE') {
              // Parent is still pending; wait for parent to finish first
              processedInThisCycle.add(tx.id);
              continue;
            }

            if (parent.status === 'DISCARDED') {
              tx.status = 'DISCARDED';
              this.appendAudit(tx, 'TRANSACTION_DISCARDED', 'Descartada: la entidad padre fue descartada.');
              await this.persist();
              this.notify();
              processedInThisCycle.add(tx.id);
              continue;
            }

            if (parent.status === 'SYNCED' && parent.permanentEntityId) {
              // Rewrite foreign keys in payload if needed
              let updatedPayload = JSON.stringify(tx.payload);
              if (updatedPayload.includes(parent.tempEntityId)) {
                updatedPayload = updatedPayload.split(parent.tempEntityId).join(parent.permanentEntityId);
                tx.payload = JSON.parse(updatedPayload);
                this.appendAudit(
                  tx,
                  'DEPENDENCY_RESOLVED',
                  `ID padre provisional (${parent.tempEntityId}) reemplazado por ID permanente (${parent.permanentEntityId}).`
                );
              }
            }
          }
        }

        // Execute transaction and mark handled in this pass
        await this.executeTransaction(tx);
        processedInThisCycle.add(tx.id);
      }
    } finally {
      this.isProcessing = false;
      await this.pruneStorage();
    }
  }

  /**
   * Executes a transaction over HTTP with stable idempotency headers.
   */
  public async executeTransaction(tx: SyncTransaction): Promise<any> {
    tx.attempts += 1;
    tx.lastAttemptAt = new Date().toISOString();

    this.appendAudit(
      tx,
      'SYNC_ATTEMPTED',
      `Intento de sincronización #${tx.attempts} contra ${tx.httpMethod} ${tx.endpoint}`
    );

    try {
      // Pass stable X-Idempotency-Key so retries are recognized by backend idempotency middleware
      const response = await apiClient<any>(tx.endpoint, {
        method: tx.httpMethod,
        headers: {
          'X-Idempotency-Key': tx.id,
        },
        body: JSON.stringify(tx.payload),
      });

      // Succeeded!
      tx.status = 'SYNCED';
      if (response && typeof response === 'object' && response.id) {
        tx.permanentEntityId = response.id;
      }

      this.appendAudit(
        tx,
        'SYNC_SUCCEEDED',
        `Sincronización confirmada exitosamente por el backend. ID permanente: ${tx.permanentEntityId || 'N/A'}`
      );

      // Unblock children
      for (const child of this.transactions.values()) {
        if (child.parentTempEntityId === tx.tempEntityId && child.status === 'BLOCKED_BY_DEPENDENCY') {
          child.status = 'PENDING';
          this.appendAudit(
            child,
            'DEPENDENCY_RESOLVED',
            `Entidad padre sincronizada. La transacción hija se reanuda automáticamente.`
          );
        }
      }

      await this.persist();
      this.notify();
      return response;
    } catch (err: any) {
      const isApiError = err instanceof ApiError;
      const status = isApiError ? err.status : 0;
      const message = err.message || 'Error de conexión desconocido';

      tx.lastError = {
        message,
        status,
        details: err,
      };

      // Conflict / Business validation error (HTTP 400, 409, 422)
      if (status === 409 || status === 422 || status === 400) {
        tx.status = 'CONFLICT_ACTION_REQUIRED';
        this.appendAudit(
          tx,
          'CONFLICT_DETECTED',
          `Fallo por regla de negocio/conflicto (${status}): "${message}". Se congela la transacción y se requiere acción del usuario.`,
          { status, message }
        );

        // Block dependent children
        for (const child of this.transactions.values()) {
          if (child.parentTempEntityId === tx.tempEntityId && child.status !== 'SYNCED' && child.status !== 'DISCARDED') {
            child.status = 'BLOCKED_BY_DEPENDENCY';
            this.appendAudit(
              child,
              'DEPENDENCY_BLOCKED',
              `Bloqueada: la entidad padre (${tx.tempEntityId}) entró en CONFLICT_ACTION_REQUIRED.`
            );
          }
        }
      } else {
        // Retryable network or server error (5xx or offline)
        tx.status = 'FAILED_RETRYABLE';
        this.appendAudit(
          tx,
          'RETRY_SCHEDULED',
          `Error de red o timeout (${status || 'Offline'}): "${message}". Se reintentará con backoff.`
        );
      }

      await this.persist();
      this.notify();
      throw err;
    }
  }

  /**
   * Scalability & Storage Pruning:
   * Keeps active items indefinitely, but caps historical archived SYNCED transactions to MAX_ARCHIVED_TRANSACTIONS.
   * Prevents AsyncStorage / LocalStorage quota exhaustion and JSON serialization latency.
   */
  private async pruneStorage(): Promise<void> {
    const syncedOrDiscarded = Array.from(this.transactions.values())
      .filter((t) => t.status === 'SYNCED' || t.status === 'DISCARDED')
      .sort((a, b) => new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime());

    if (syncedOrDiscarded.length > MAX_ARCHIVED_TRANSACTIONS) {
      const toRemove = syncedOrDiscarded.slice(0, syncedOrDiscarded.length - MAX_ARCHIVED_TRANSACTIONS);
      for (const item of toRemove) {
        this.transactions.delete(item.id);
      }
      await this.persist();
    }
  }

  /**
   * Diagnostic exporter: full transactional trace for support and debugging.
   */
  public exportDiagnostics(): string {
    const data = Array.from(this.transactions.values());
    return JSON.stringify(
      {
        exportedAt: new Date().toISOString(),
        totalTransactions: data.length,
        summaryByStatus: {
          PENDING: data.filter((t) => t.status === 'PENDING').length,
          SYNCED: data.filter((t) => t.status === 'SYNCED').length,
          FAILED_RETRYABLE: data.filter((t) => t.status === 'FAILED_RETRYABLE').length,
          CONFLICT_ACTION_REQUIRED: data.filter((t) => t.status === 'CONFLICT_ACTION_REQUIRED').length,
          BLOCKED_BY_DEPENDENCY: data.filter((t) => t.status === 'BLOCKED_BY_DEPENDENCY').length,
          DISCARDED: data.filter((t) => t.status === 'DISCARDED').length,
        },
        transactions: data,
      },
      null,
      2
    );
  }
}

export const syncLedger = new SyncLedgerManager();
