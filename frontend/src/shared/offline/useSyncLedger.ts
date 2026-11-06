import { useState, useEffect, useCallback } from 'react';
import { syncLedger, SyncTransaction } from './syncLedger';
import { useIsOnline } from './offlineManager';

export function useSyncTransactions() {
  const [transactions, setTransactions] = useState<SyncTransaction[]>(() =>
    syncLedger.getAllTransactions()
  );
  const isOnline = useIsOnline();

  useEffect(() => {
    // Initial fetch
    setTransactions(syncLedger.getAllTransactions());

    // Subscribe to ledger changes
    const unsubscribe = syncLedger.subscribe(() => {
      setTransactions(syncLedger.getAllTransactions());
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // When connection restores, trigger queue processing automatically
  useEffect(() => {
    if (isOnline) {
      syncLedger.processQueue().catch(() => {});
    }
  }, [isOnline]);

  const resolveConflict = useCallback(
    async <T extends Record<string, any>>(transactionId: string, updatedPayload: Partial<T>) => {
      return syncLedger.resolveConflict(transactionId, updatedPayload);
    },
    []
  );

  const discardTransaction = useCallback(
    async (transactionId: string, reason?: string) => {
      return syncLedger.discardTransaction(transactionId, reason);
    },
    []
  );

  const retryQueue = useCallback(async () => {
    return syncLedger.processQueue();
  }, []);

  const exportDiagnostics = useCallback(() => {
    return syncLedger.exportDiagnostics();
  }, []);

  const pendingCount = transactions.filter(
    (t) => t.status === 'PENDING' || t.status === 'FAILED_RETRYABLE'
  ).length;

  const conflictCount = transactions.filter(
    (t) => t.status === 'CONFLICT_ACTION_REQUIRED'
  ).length;

  const blockedCount = transactions.filter(
    (t) => t.status === 'BLOCKED_BY_DEPENDENCY'
  ).length;

  return {
    transactions,
    pendingCount,
    conflictCount,
    blockedCount,
    resolveConflict,
    discardTransaction,
    retryQueue,
    exportDiagnostics,
  };
}

export function useSyncTransactionForEntity(tempEntityId?: string) {
  const [transaction, setTransaction] = useState<SyncTransaction | undefined>(() =>
    tempEntityId ? syncLedger.getByTempId(tempEntityId) : undefined
  );

  useEffect(() => {
    if (!tempEntityId) {
      setTransaction(undefined);
      return;
    }

    setTransaction(syncLedger.getByTempId(tempEntityId));
    const unsubscribe = syncLedger.subscribe(() => {
      setTransaction(syncLedger.getByTempId(tempEntityId));
    });

    return () => {
      unsubscribe();
    };
  }, [tempEntityId]);

  return transaction;
}
