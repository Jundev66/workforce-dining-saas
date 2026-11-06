import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Employee } from '../model/employeeTypes';
import { Badge } from '../../../shared/components/Badge';
import { colors } from '../../../shared/theme/colors';

interface EmployeeCardProps {
  employee: Employee;
  onPress: (employee: Employee) => void;
}

export const EmployeeCard: React.FC<EmployeeCardProps> = React.memo(({
  employee,
  onPress,
}) => {
  const isConflict = employee.sync_status === 'CONFLICT_ACTION_REQUIRED';
  const isBlocked = employee.sync_status === 'BLOCKED_BY_DEPENDENCY';
  const isPending = employee.sync_status === 'PENDING' || employee.sync_status === 'FAILED_RETRYABLE';

  return (
    <TouchableOpacity
      activeOpacity={0.7}
      style={[
        styles.card,
        isConflict ? styles.cardConflict : isBlocked ? styles.cardBlocked : null,
      ]}
      onPress={() => onPress(employee)}
      testID={`employee-card-${employee.id}`}
    >
      <View style={styles.headerRow}>
        <View style={styles.infoCol}>
          <Text style={styles.name} numberOfLines={1}>
            {employee.full_name}
          </Text>
          <Text style={styles.document}>Doc: {employee.document_id}</Text>
        </View>
        <View style={styles.badgeContainer}>
          {employee.sync_status && employee.sync_status !== 'SYNCED' ? (
            <Badge status={employee.sync_status} />
          ) : (
            <Badge status={employee.status} />
          )}
        </View>
      </View>

      {/* Actionable offline status banner */}
      {isConflict ? (
        <View style={styles.conflictBanner} testID={`conflict-banner-${employee.id}`}>
          <Text style={styles.conflictBannerText}>
            ⚠️ Conflicto: {employee.sync_error || 'Datos rechazados por el servidor'}. Toca para corregir.
          </Text>
        </View>
      ) : isBlocked ? (
        <View style={styles.blockedBanner} testID={`blocked-banner-${employee.id}`}>
          <Text style={styles.blockedBannerText}>
            ⏳ Pausado: Esperando confirmación de la entidad padre.
          </Text>
        </View>
      ) : isPending ? (
        <View style={styles.pendingBanner} testID={`pending-banner-${employee.id}`}>
          <Text style={styles.pendingBannerText}>
            📡 Guardado en dispositivo. Se sincronizará automáticamente.
          </Text>
        </View>
      ) : null}

      <View style={styles.detailRow}>
        <View style={styles.tag}>
          <Text style={styles.tagLabel}>Depto:</Text>
          <Text style={styles.tagValue}>{employee.department}</Text>
        </View>

        <View style={styles.tag}>
          <Text style={styles.tagLabel}>Cargo:</Text>
          <Text style={styles.tagValue}>{employee.position}</Text>
        </View>
      </View>

      <View style={styles.footerRow}>
        <Text style={styles.badgeCode}>Credencial: {employee.badge_code}</Text>
        {employee.id.startsWith('temp-') && (
          <Text style={styles.tempBadge}>Borrador local</Text>
        )}
      </View>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  cardConflict: {
    borderColor: '#fca5a5',
    backgroundColor: '#fffafa',
  },
  cardBlocked: {
    borderColor: '#d8b4fe',
    backgroundColor: '#faf5ff',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  infoCol: {
    flex: 1,
    marginRight: 8,
  },
  badgeContainer: {
    alignItems: 'flex-end',
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 2,
  },
  document: {
    fontSize: 13,
    color: '#64748b',
    fontWeight: '500',
  },
  conflictBanner: {
    backgroundColor: '#fef2f2',
    borderLeftWidth: 3,
    borderLeftColor: '#ef4444',
    padding: 8,
    borderRadius: 6,
    marginBottom: 10,
  },
  conflictBannerText: {
    fontSize: 12,
    color: '#b91c1c',
    fontWeight: '600',
  },
  blockedBanner: {
    backgroundColor: '#f3e8ff',
    borderLeftWidth: 3,
    borderLeftColor: '#9333ea',
    padding: 8,
    borderRadius: 6,
    marginBottom: 10,
  },
  blockedBannerText: {
    fontSize: 12,
    color: '#7e22ce',
    fontWeight: '600',
  },
  pendingBanner: {
    backgroundColor: '#fefce8',
    borderLeftWidth: 3,
    borderLeftColor: '#ca8a04',
    padding: 6,
    borderRadius: 6,
    marginBottom: 10,
  },
  pendingBannerText: {
    fontSize: 11,
    color: '#854d0e',
    fontWeight: '500',
  },
  detailRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f1f5f9',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  tagLabel: {
    fontSize: 12,
    color: '#64748b',
    marginRight: 4,
    fontWeight: '500',
  },
  tagValue: {
    fontSize: 12,
    color: '#1e293b',
    fontWeight: '600',
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 10,
  },
  badgeCode: {
    fontSize: 12,
    color: '#475569',
    fontWeight: '600',
    fontFamily: 'monospace',
  },
  tempBadge: {
    fontSize: 11,
    color: '#b45309',
    backgroundColor: '#fef3c7',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    fontWeight: '600',
  },
});
