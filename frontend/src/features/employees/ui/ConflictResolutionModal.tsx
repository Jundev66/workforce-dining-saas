import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
} from 'react-native';
import { Employee } from '../model/employeeTypes';
import { syncLedger } from '../../../shared/offline/syncLedger';
import { useSyncTransactionForEntity } from '../../../shared/offline/useSyncLedger';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

interface ConflictResolutionModalProps {
  employee: Employee | null;
  visible: boolean;
  onClose: () => void;
  onResolved?: () => void;
}

export const ConflictResolutionModal: React.FC<ConflictResolutionModalProps> = ({
  employee,
  visible,
  onClose,
  onResolved,
}) => {
  const transaction = useSyncTransactionForEntity(employee?.id);
  const [docId, setDocId] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [copiedAudit, setCopiedAudit] = useState(false);

  React.useEffect(() => {
    if (employee && transaction) {
      setDocId(transaction.payload.document_id || employee.document_id || '');
      setFirstName(transaction.payload.first_name || employee.first_name || '');
      setLastName(transaction.payload.last_name || employee.last_name || '');
    }
  }, [employee, transaction]);

  if (!employee || !visible) return null;

  const isConflict =
    employee.sync_status === 'CONFLICT_ACTION_REQUIRED' ||
    transaction?.status === 'CONFLICT_ACTION_REQUIRED';
  const isBlocked =
    employee.sync_status === 'BLOCKED_BY_DEPENDENCY' ||
    transaction?.status === 'BLOCKED_BY_DEPENDENCY';

  const handleRetryWithCorrection = async () => {
    if (!transaction) return;
    await syncLedger.resolveConflict(transaction.id, {
      document_id: docId.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
    });
    if (onResolved) onResolved();
    onClose();
  };

  const handleDiscard = async () => {
    if (!transaction) return;
    await syncLedger.discardTransaction(transaction.id, 'Descarte manual tras conflicto');
    if (onResolved) onResolved();
    onClose();
  };

  const auditJson = transaction ? JSON.stringify(transaction.auditTrail, null, 2) : '';

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.card} testID="modal-conflict-resolution">
          <View style={styles.header}>
            <View style={styles.titleContainer}>
              <Text style={styles.title}>
                {isConflict
                  ? '⚠️ Conflicto de Sincronización'
                  : isBlocked
                  ? '⏳ Bloqueado por Dependencia'
                  : 'Borrador sin Sincronizar'}
              </Text>
              <Text style={styles.subtitle}>ID Provisional: {employee.id}</Text>
            </View>
            <TouchableOpacity onPress={onClose} testID="btn-close-conflict-modal">
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* Conflict or blocked alert banner */}
            <View
              style={[
                styles.alertBanner,
                isConflict ? styles.alertDanger : styles.alertWarning,
              ]}
            >
              <Text style={styles.alertTitle}>
                {isConflict ? 'Error de validación / unicidad' : 'En espera de entidad padre'}
              </Text>
              <Text style={styles.alertText}>
                {transaction?.lastError?.message ||
                  employee.sync_error ||
                  (isBlocked
                    ? 'Esta acción depende de un registro padre que aún no fue confirmado.'
                    : 'La transacción no pudo confirmarse en el servidor.')}
              </Text>
              {transaction?.lastError?.status ? (
                <Text style={styles.alertCode}>
                  Código HTTP: {transaction.lastError.status}
                </Text>
              ) : null}
            </View>

            {/* Editable Fields for Resolution */}
            {isConflict ? (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Corregir datos del empleado:</Text>

                <Text style={styles.label}>Número de Documento (DNI/CI):</Text>
                <TextInput
                  testID="input-correct-doc"
                  style={styles.input}
                  value={docId}
                  onChangeText={setDocId}
                  placeholder="Ej: 12345678"
                />

                <Text style={styles.label}>Nombre:</Text>
                <TextInput
                  testID="input-correct-firstname"
                  style={styles.input}
                  value={firstName}
                  onChangeText={setFirstName}
                />

                <Text style={styles.label}>Apellido:</Text>
                <TextInput
                  testID="input-correct-lastname"
                  style={styles.input}
                  value={lastName}
                  onChangeText={setLastName}
                />

                <Button
                  testID="btn-save-conflict-fix"
                  title="Corregir y Reintentar Sincronización"
                  onPress={handleRetryWithCorrection}
                  variant="primary"
                  style={styles.actionBtn}
                />
              </View>
            ) : null}

            {/* Discard option */}
            <View style={styles.section}>
              <Button
                testID="btn-discard-draft"
                title="Descartar Borrador (Rollback Seguro)"
                onPress={handleDiscard}
                variant="danger"
                style={styles.discardBtn}
              />
              <Text style={styles.helperText}>
                Al descartar, se cancelará la operación y se registrará la transacción en el historial de auditoría.
              </Text>
            </View>

            {/* Audit Trail Section for Debugging */}
            <View style={styles.section}>
              <TouchableOpacity
                onPress={() => setShowAuditTrail(!showAuditTrail)}
                style={styles.toggleAuditBtn}
                testID="btn-toggle-audit"
              >
                <Text style={styles.toggleAuditText}>
                  {showAuditTrail ? '▼ Ocultar Trazabilidad (Auditoría)' : '▶ Ver Trazabilidad de Transacción (Debug)'}
                </Text>
              </TouchableOpacity>

              {showAuditTrail && transaction && (
                <View style={styles.auditContainer} testID="audit-trail-container">
                  <Text style={styles.auditHeader}>Historial de Eventos (Ledger Log):</Text>
                  {transaction.auditTrail.map((ev, idx) => (
                    <View key={ev.id || idx} style={styles.auditRow}>
                      <Text style={styles.auditTime}>
                        {new Date(ev.timestamp).toLocaleTimeString()} -{' '}
                        <Text style={styles.auditEvent}>{ev.event}</Text>
                      </Text>
                      <Text style={styles.auditDetails}>{ev.details}</Text>
                    </View>
                  ))}

                  <TouchableOpacity
                    style={styles.copyJsonBtn}
                    onPress={() => {
                      if (typeof navigator !== 'undefined' && navigator.clipboard) {
                        navigator.clipboard.writeText(auditJson);
                      }
                      setCopiedAudit(true);
                      setTimeout(() => setCopiedAudit(false), 2000);
                    }}
                  >
                    <Text style={styles.copyJsonText}>
                      {copiedAudit ? '✓ Copiado al portapapeles' : 'Copiar Diagnóstico JSON'}
                    </Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.65)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    width: '100%',
    maxWidth: 520,
    maxHeight: '90%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  titleContainer: {
    flex: 1,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
    fontFamily: 'monospace',
  },
  closeBtn: {
    fontSize: 18,
    color: colors.textMuted,
    padding: 4,
  },
  content: {
    padding: 20,
  },
  alertBanner: {
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  alertDanger: {
    backgroundColor: '#fef2f2',
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444',
  },
  alertWarning: {
    backgroundColor: '#fffbeb',
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  alertTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#991b1b',
    marginBottom: 4,
  },
  alertText: {
    fontSize: 13,
    color: '#7f1d1d',
    lineHeight: 18,
  },
  alertCode: {
    fontSize: 11,
    fontWeight: '600',
    color: '#991b1b',
    marginTop: 4,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 10,
  },
  label: {
    fontSize: 13,
    fontWeight: '500',
    color: colors.textMuted,
    marginBottom: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    color: colors.text,
    marginBottom: 12,
    backgroundColor: '#f8fafc',
  },
  actionBtn: {
    marginTop: 8,
  },
  discardBtn: {
    borderColor: '#ef4444',
  },
  helperText: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 6,
    textAlign: 'center',
  },
  toggleAuditBtn: {
    paddingVertical: 8,
  },
  toggleAuditText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
  auditContainer: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
  },
  auditHeader: {
    fontSize: 12,
    fontWeight: '700',
    color: '#94a3b8',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  auditRow: {
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
    paddingVertical: 6,
  },
  auditTime: {
    fontSize: 11,
    color: '#64748b',
    fontFamily: 'monospace',
  },
  auditEvent: {
    color: '#38bdf8',
    fontWeight: '700',
  },
  auditDetails: {
    fontSize: 12,
    color: '#e2e8f0',
    marginTop: 2,
  },
  copyJsonBtn: {
    marginTop: 10,
    backgroundColor: '#1e293b',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  copyJsonText: {
    fontSize: 11,
    color: '#f8fafc',
    fontWeight: '600',
  },
});
