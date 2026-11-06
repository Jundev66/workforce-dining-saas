import test from 'node:test';
import assert from 'node:assert/strict';

// Test the pure state machine and causal dependency resolution logic of SyncLedger
test('Sync Ledger State Machine & Dependency Saga Suite', async (t) => {
  // In-memory ledger model matching our syncLedger architecture
  const memoryStore = new Map();
  const transactions = new Map();

  function createUUID() {
    return 'tx-' + Math.random().toString(36).substring(2, 9);
  }

  function appendAudit(tx, event, details, metadata) {
    const entry = {
      id: createUUID(),
      timestamp: new Date().toISOString(),
      event,
      details,
      metadata,
    };
    tx.auditTrail.push(entry);
    tx.updatedAt = entry.timestamp;
  }

  function enqueue(params) {
    const id = createUUID();
    const now = new Date().toISOString();
    let initialStatus = 'PENDING';

    const parent = params.parentTempEntityId ? transactions.get(params.parentTempEntityId) : null;
    if (parent && (parent.status === 'CONFLICT_ACTION_REQUIRED' || parent.status === 'BLOCKED_BY_DEPENDENCY')) {
      initialStatus = 'BLOCKED_BY_DEPENDENCY';
    }

    const tx = {
      id,
      entityType: params.entityType,
      tempEntityId: params.tempEntityId,
      parentTempEntityId: params.parentTempEntityId,
      action: params.action,
      payload: params.payload,
      status: initialStatus,
      attempts: 0,
      createdAt: now,
      updatedAt: now,
      auditTrail: [],
    };

    appendAudit(tx, 'TRANSACTION_CREATED', `Enqueued ${params.action} ${params.entityType}`);
    if (initialStatus === 'BLOCKED_BY_DEPENDENCY') {
      appendAudit(tx, 'DEPENDENCY_BLOCKED', `Blocked by parent ${params.parentTempEntityId}`);
    }

    transactions.set(params.tempEntityId, tx);
    return tx;
  }

  function markConflict(tempId, errorMsg, statusCode) {
    const tx = transactions.get(tempId);
    if (!tx) return;
    tx.status = 'CONFLICT_ACTION_REQUIRED';
    tx.lastError = { message: errorMsg, status: statusCode };
    appendAudit(tx, 'CONFLICT_DETECTED', `Conflict ${statusCode}: ${errorMsg}`);

    // Cascade block to children
    for (const child of transactions.values()) {
      if (child.parentTempEntityId === tx.tempEntityId && child.status !== 'SYNCED' && child.status !== 'DISCARDED') {
        child.status = 'BLOCKED_BY_DEPENDENCY';
        appendAudit(child, 'DEPENDENCY_BLOCKED', `Blocked because parent ${tx.tempEntityId} entered conflict`);
      }
    }
  }

  function resolveConflict(tempId, correctedPayload) {
    const tx = transactions.get(tempId);
    if (!tx) return;
    tx.payload = { ...tx.payload, ...correctedPayload };
    tx.status = 'PENDING';
    tx.lastError = undefined;
    appendAudit(tx, 'CONFLICT_PAYLOAD_UPDATED', 'User corrected data');
  }

  function markSynced(tempId, permanentId) {
    const tx = transactions.get(tempId);
    if (!tx) return;
    tx.status = 'SYNCED';
    tx.permanentEntityId = permanentId;
    appendAudit(tx, 'SYNC_SUCCEEDED', `Confirmed with server ID ${permanentId}`);

    // Unblock children and rewrite FK
    for (const child of transactions.values()) {
      if (child.parentTempEntityId === tx.tempEntityId && child.status === 'BLOCKED_BY_DEPENDENCY') {
        child.status = 'PENDING';
        let str = JSON.stringify(child.payload);
        str = str.split(tx.tempEntityId).join(permanentId);
        child.payload = JSON.parse(str);
        appendAudit(child, 'DEPENDENCY_RESOLVED', `Unblocked & updated FK to ${permanentId}`);
      }
    }
  }

  function discardTransaction(tempId, reason) {
    const tx = transactions.get(tempId);
    if (!tx) return;
    tx.status = 'DISCARDED';
    appendAudit(tx, 'TRANSACTION_DISCARDED', reason);

    for (const child of transactions.values()) {
      if (child.parentTempEntityId === tx.tempEntityId && child.status !== 'SYNCED' && child.status !== 'DISCARDED') {
        child.status = 'DISCARDED';
        appendAudit(child, 'TRANSACTION_DISCARDED', `Cascade discard from parent ${tx.tempEntityId}`);
      }
    }
  }

  await t.test('1. Enqueue parent (Employee) and child (Meal Scan)', () => {
    const emp = enqueue({
      entityType: 'employee',
      tempEntityId: 'temp-emp-001',
      action: 'CREATE',
      payload: { firstName: 'Carlos', lastName: 'Lopez', documentId: 'DNI-123' },
    });

    const meal = enqueue({
      entityType: 'dining_scan',
      tempEntityId: 'temp-meal-001',
      parentTempEntityId: 'temp-emp-001',
      action: 'CREATE',
      payload: { employeeId: 'temp-emp-001', mealType: 'lunch' },
    });

    assert.equal(emp.status, 'PENDING');
    assert.equal(meal.status, 'PENDING');
    assert.equal(emp.auditTrail[0].event, 'TRANSACTION_CREATED');
    assert.equal(meal.auditTrail[0].event, 'TRANSACTION_CREATED');
  });

  await t.test('2. Parent failure with HTTP 409 Conflict triggers CONFLICT_ACTION_REQUIRED and blocks child', () => {
    markConflict('temp-emp-001', 'DNI-123 duplicado en nómina', 409);

    const emp = transactions.get('temp-emp-001');
    const meal = transactions.get('temp-meal-001');

    assert.equal(emp.status, 'CONFLICT_ACTION_REQUIRED');
    assert.equal(emp.lastError.status, 409);
    assert.equal(meal.status, 'BLOCKED_BY_DEPENDENCY');

    // Verify audit logs exist and describe the event
    const lastEmpEvent = emp.auditTrail[emp.auditTrail.length - 1];
    assert.equal(lastEmpEvent.event, 'CONFLICT_DETECTED');

    const lastMealEvent = meal.auditTrail[meal.auditTrail.length - 1];
    assert.equal(lastMealEvent.event, 'DEPENDENCY_BLOCKED');
  });

  await t.test('3. Enqueuing new child while parent is in conflict starts immediately as BLOCKED_BY_DEPENDENCY', () => {
    const attendance = enqueue({
      entityType: 'attendance',
      tempEntityId: 'temp-att-001',
      parentTempEntityId: 'temp-emp-001',
      action: 'CREATE',
      payload: { employeeId: 'temp-emp-001', checkIn: '08:00' },
    });

    assert.equal(attendance.status, 'BLOCKED_BY_DEPENDENCY');
    assert.equal(attendance.auditTrail.some((e) => e.event === 'DEPENDENCY_BLOCKED'), true);
  });

  await t.test('4. Resolving conflict and confirming parent unblocks children and rewrites FK', () => {
    // User fixes the DNI
    resolveConflict('temp-emp-001', { documentId: 'DNI-999-CORRECT' });
    const emp = transactions.get('temp-emp-001');
    assert.equal(emp.status, 'PENDING');
    assert.equal(emp.payload.documentId, 'DNI-999-CORRECT');

    // Backend confirms and returns real permanent UUID
    markSynced('temp-emp-001', 'real-uuid-carlos');
    assert.equal(emp.status, 'SYNCED');
    assert.equal(emp.permanentEntityId, 'real-uuid-carlos');

    // Children should be unblocked and FK rewritten!
    const meal = transactions.get('temp-meal-001');
    assert.equal(meal.status, 'PENDING');
    assert.equal(meal.payload.employeeId, 'real-uuid-carlos');
    assert.equal(meal.auditTrail.some((e) => e.event === 'DEPENDENCY_RESOLVED'), true);

    const att = transactions.get('temp-att-001');
    assert.equal(att.status, 'PENDING');
    assert.equal(att.payload.employeeId, 'real-uuid-carlos');
  });

  await t.test('5. Discard cascade flow cancels parent and blocked dependent entities', () => {
    // Create new parent and child
    enqueue({
      entityType: 'employee',
      tempEntityId: 'temp-emp-to-discard',
      action: 'CREATE',
      payload: { documentId: 'DNI-BAD' },
    });
    enqueue({
      entityType: 'dining_scan',
      tempEntityId: 'temp-meal-to-discard',
      parentTempEntityId: 'temp-emp-to-discard',
      action: 'CREATE',
      payload: { employeeId: 'temp-emp-to-discard' },
    });

    markConflict('temp-emp-to-discard', 'Fatal corruption', 422);
    discardTransaction('temp-emp-to-discard', 'Usuario canceló registro');

    const parent = transactions.get('temp-emp-to-discard');
    const child = transactions.get('temp-meal-to-discard');

    assert.equal(parent.status, 'DISCARDED');
    assert.equal(child.status, 'DISCARDED');
    assert.equal(child.auditTrail.some((e) => e.event === 'TRANSACTION_DISCARDED'), true);
  });
});
