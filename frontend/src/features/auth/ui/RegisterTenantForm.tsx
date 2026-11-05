import React, { useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { registerTenantSchema, RegisterTenantFormData } from '../model/authSchemas';
import { authApi } from '../api/authApi';
import { useAuthStore } from '../model/authStore';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

interface RegisterTenantFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterTenantForm: React.FC<RegisterTenantFormProps> = ({
  onSuccess,
  onSwitchToLogin,
}) => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const setSession = useAuthStore((state) => state.setSession);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterTenantFormData>({
    resolver: zodResolver(registerTenantSchema),
    defaultValues: {
      tenantName: '',
      tenantSlug: '',
      adminFullName: '',
      adminEmail: '',
      adminPassword: '',
    },
  });

  const onSubmit = async (data: RegisterTenantFormData) => {
    setErrorMsg(null);
    setIsLoading(true);
    try {
      const { token, user } = await authApi.registerTenant(data);
      setSession(token, user);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al registrar la empresa');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.card} testID="register-tenant-card">
      <Text style={styles.title}>Registrar Empresa</Text>
      <Text style={styles.subtitle}>Onboarding Multi-Tenant SaaS</Text>

      {errorMsg ? (
        <View style={styles.errorBanner} testID="register-error-banner">
          <Text style={styles.errorBannerText}>{errorMsg}</Text>
        </View>
      ) : null}

      <Controller
        control={control}
        name="tenantName"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-register-name"
            label="Nombre de la Empresa *"
            placeholder="Ej: Catering & Servicios S.A."
            value={value}
            onChangeText={onChange}
            error={errors.tenantName?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="tenantSlug"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-register-slug"
            label="Identificador único (slug) *"
            placeholder="catering-servicios"
            value={value}
            onChangeText={onChange}
            autoCapitalize="none"
            error={errors.tenantSlug?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="adminFullName"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-register-admin-name"
            label="Nombre del Administrador *"
            placeholder="Ej: Marcelo Gallardo"
            value={value}
            onChangeText={onChange}
            error={errors.adminFullName?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="adminEmail"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-register-admin-email"
            label="Email del Administrador *"
            placeholder="admin@empresa.com"
            value={value}
            onChangeText={onChange}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.adminEmail?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="adminPassword"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-register-admin-password"
            label="Contraseña (mínimo 8 caracteres) *"
            placeholder="••••••••"
            value={value}
            onChangeText={onChange}
            secureTextEntry
            error={errors.adminPassword?.message}
          />
        )}
      />

      <Button
        testID="btn-submit-register"
        title="Crear Organización"
        onPress={() => handleSubmit(onSubmit)()}
        isLoading={isLoading}
        style={styles.submitBtn}
      />

      {onSwitchToLogin && (
        <Button
          testID="btn-switch-login"
          title="Ya tengo cuenta (Iniciar Sesión)"
          variant="secondary"
          onPress={onSwitchToLogin}
          style={styles.loginBtn}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    padding: 24,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    width: '100%',
    maxWidth: 420,
    alignSelf: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.text,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: colors.textMuted,
    textAlign: 'center',
    marginBottom: 20,
    marginTop: 4,
  },
  errorBanner: {
    backgroundColor: colors.dangerLight,
    padding: 10,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorBannerText: {
    color: colors.danger,
    fontSize: 13,
    textAlign: 'center',
    fontWeight: '500',
  },
  submitBtn: {
    marginTop: 8,
  },
  loginBtn: {
    marginTop: 12,
  },
});
