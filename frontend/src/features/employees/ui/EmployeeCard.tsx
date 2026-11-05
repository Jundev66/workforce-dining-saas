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
  return (
    <TouchableOpacity
      activeOpacity={0.7}
      style={styles.card}
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
        <Badge status={employee.status} />
      </View>

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
      </View>
    </TouchableOpacity>
  );
});

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  infoCol: {
    flex: 1,
    marginRight: 10,
  },
  name: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
  },
  document: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 2,
  },
  detailRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 8,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  tagLabel: {
    fontSize: 12,
    color: colors.textMuted,
  },
  tagValue: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.text,
  },
  footerRow: {
    borderTopWidth: 1,
    borderTopColor: colors.surfaceSubtle,
    paddingTop: 8,
    marginTop: 4,
  },
  badgeCode: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
  },
});
