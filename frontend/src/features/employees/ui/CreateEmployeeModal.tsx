import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { employeeFormSchema, EmployeeFormData } from '../model/employeeSchemas';
import { useCreateEmployeeMutation } from '../api/employeeApi';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

interface CreateEmployeeModalProps {
  visible: boolean;
  onClose: () => void;
}

export const CreateEmployeeModal: React.FC<CreateEmployeeModalProps> = ({
  visible,
  onClose,
}) => {
  const [apiError, setApiError] = useState<string | null>(null);
  const createMutation = useCreateEmployeeMutation();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EmployeeFormData>({
    resolver: zodResolver(employeeFormSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      documentId: '',
      department: 'Operaciones',
      position: 'Operador',
      email: '',
      phone: '',
      badgeCode: '',
    },
  });

  const onSubmit = async (data: EmployeeFormData) => {
    setApiError(null);
    try {
      await createMutation.mutateAsync(data);
      reset();
      onClose();
    } catch (err: any) {
      setApiError(err.message || 'Error al crear el empleado');
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.modalCard} testID="modal-create-employee">
          <View style={styles.header}>
            <Text style={styles.title}>Nuevo Empleado</Text>
            <TouchableOpacity onPress={onClose} testID="btn-close-modal">
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>

          {apiError ? (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{apiError}</Text>
            </View>
          ) : null}

          <ScrollView style={styles.formScroll} showsVerticalScrollIndicator={false}>
            <Controller
              control={control}
              name="firstName"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-firstname"
                  label="Nombre *"
                  placeholder="Ej: Carlos"
                  value={value}
                  onChangeText={onChange}
                  error={errors.firstName?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="lastName"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-lastname"
                  label="Apellido *"
                  placeholder="Ej: Gomez"
                  value={value}
                  onChangeText={onChange}
                  error={errors.lastName?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="documentId"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-document"
                  label="Documento de Identidad *"
                  placeholder="Ej: DNI-35890123"
                  value={value}
                  onChangeText={onChange}
                  error={errors.documentId?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="department"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-department"
                  label="Departamento *"
                  placeholder="Ej: Cocina, Mantenimiento"
                  value={value}
                  onChangeText={onChange}
                  error={errors.department?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="position"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-position"
                  label="Cargo *"
                  placeholder="Ej: Chef Ejecutivo"
                  value={value}
                  onChangeText={onChange}
                  error={errors.position?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="badgeCode"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-badge"
                  label="Código de Credencial / QR (Opcional)"
                  placeholder="Dejar vacío para autogenerar"
                  value={value}
                  onChangeText={onChange}
                />
              )}
            />

            <Controller
              control={control}
              name="email"
              render={({ field: { onChange, value } }) => (
                <Input
                  testID="input-employee-email"
                  label="Email (Opcional)"
                  placeholder="carlos.gomez@empresa.com"
                  value={value}
                  onChangeText={onChange}
                  keyboardType="email-address"
                  error={errors.email?.message}
                />
              )}
            />

            <View style={styles.actionsRow}>
              <Button
                title="Cancelar"
                variant="secondary"
                onPress={onClose}
                style={styles.cancelBtn}
              />
              <Button
                testID="btn-submit-employee"
                title="Registrar"
                onPress={() => handleSubmit(onSubmit)()}
                isLoading={createMutation.isPending}
                style={styles.saveBtn}
              />
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
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  modalCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    width: '100%',
    maxWidth: 480,
    maxHeight: '90%',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
  },
  closeBtn: {
    fontSize: 18,
    color: colors.textMuted,
    padding: 4,
  },
  errorBox: {
    backgroundColor: colors.dangerLight,
    padding: 10,
    borderRadius: 8,
    marginBottom: 12,
  },
  errorText: {
    color: colors.danger,
    fontSize: 13,
  },
  formScroll: {
    maxHeight: 520,
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
    marginBottom: 8,
  },
  cancelBtn: {
    flex: 1,
  },
  saveBtn: {
    flex: 1,
  },
});
