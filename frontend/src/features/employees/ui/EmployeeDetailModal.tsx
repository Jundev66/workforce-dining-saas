import React from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { Employee } from '../model/employeeTypes';
import {
  useUpdateEmployeeMutation,
  useDeleteEmployeeMutation,
} from '../api/employeeApi';
import { Badge } from '../../../shared/components/Badge';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

interface EmployeeDetailModalProps {
  employee: Employee | null;
  visible: boolean;
  onClose: () => void;
}

export const EmployeeDetailModal: React.FC<EmployeeDetailModalProps> = ({
  employee,
  visible,
  onClose,
}) => {
  const updateMutation = useUpdateEmployeeMutation();
  const deleteMutation = useDeleteEmployeeMutation();

  if (!employee) return null;

  const handleToggleStatus = async () => {
    const nextStatus = employee.status === 'active' ? 'inactive' : 'active';
    await updateMutation.mutateAsync({
      id: employee.id,
      data: { status: nextStatus },
    });
    onClose();
  };

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(employee.id);
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="fade"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.card} testID="modal-employee-detail">
          <View style={styles.header}>
            <View>
              <Text style={styles.name}>{employee.full_name}</Text>
              <Text style={styles.doc}>Doc: {employee.document_id}</Text>
            </View>
            <TouchableOpacity onPress={onClose} testID="btn-close-detail">
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.body}>
            <View style={styles.row}>
              <Text style={styles.label}>Estado:</Text>
              <Badge status={employee.status} />
            </View>

            <View style={styles.row}>
              <Text style={styles.label}>Departamento:</Text>
              <Text style={styles.value}>{employee.department}</Text>
            </View>

            <View style={styles.row}>
              <Text style={styles.label}>Cargo:</Text>
              <Text style={styles.value}>{employee.position}</Text>
            </View>

            <View style={styles.row}>
              <Text style={styles.label}>Credencial / QR:</Text>
              <Text style={[styles.value, styles.badgeText]}>{employee.badge_code}</Text>
            </View>

            {employee.email ? (
              <View style={styles.row}>
                <Text style={styles.label}>Email:</Text>
                <Text style={styles.value}>{employee.email}</Text>
              </View>
            ) : null}

            {employee.phone ? (
              <View style={styles.row}>
                <Text style={styles.label}>Teléfono:</Text>
                <Text style={styles.value}>{employee.phone}</Text>
              </View>
            ) : null}
          </View>

          <View style={styles.actions}>
            <Button
              testID="btn-toggle-status"
              title={employee.status === 'active' ? 'Dar de Baja (Inactivar)' : 'Reactivar Empleado'}
              variant="secondary"
              onPress={handleToggleStatus}
              isLoading={updateMutation.isPending}
              style={styles.actionBtn}
            />

            <Button
              testID="btn-delete-employee"
              title="Eliminar Registro"
              variant="danger"
              onPress={handleDelete}
              isLoading={deleteMutation.isPending}
              style={styles.actionBtn}
            />
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    width: '100%',
    maxWidth: 440,
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: 12,
    marginBottom: 16,
  },
  name: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.text,
  },
  doc: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 2,
  },
  closeBtn: {
    fontSize: 18,
    color: colors.textMuted,
    padding: 4,
  },
  body: {
    gap: 12,
    marginBottom: 20,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  label: {
    fontSize: 14,
    color: colors.textMuted,
  },
  value: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  badgeText: {
    color: colors.primary,
  },
  actions: {
    gap: 10,
  },
  actionBtn: {
    width: '100%',
  },
});
