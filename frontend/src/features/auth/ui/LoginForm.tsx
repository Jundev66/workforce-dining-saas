import React, { useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '../model/authSchemas';
import { authApi } from '../api/authApi';
import { useAuthStore } from '../model/authStore';
import { Input } from '../../../shared/components/Input';
import { Button } from '../../../shared/components/Button';
import { colors } from '../../../shared/theme/colors';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
}) => {
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const setSession = useAuthStore((state) => state.setSession);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      tenantSlug: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setErrorMsg(null);
    setIsLoading(true);
    try {
      const { token, user } = await authApi.login(data);
      setSession(token, user);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.card} testID="login-card">
      <Text style={styles.title}>Iniciar Sesión</Text>
      <Text style={styles.subtitle}>Gestión de Personal & Comedores</Text>

      {errorMsg ? (
        <View style={styles.errorBanner} testID="login-error-banner">
          <Text style={styles.errorBannerText}>{errorMsg}</Text>
        </View>
      ) : null}

      <Controller
        control={control}
        name="tenantSlug"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-tenant-slug"
            label="Identificador de Empresa (Opcional)"
            placeholder="acme"
            value={value}
            onChangeText={onChange}
            autoCapitalize="none"
          />
        )}
      />

      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-email"
            label="Correo Electrónico"
            placeholder="admin@empresa.com"
            value={value}
            onChangeText={onChange}
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.email?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, value } }) => (
          <Input
            testID="input-password"
            label="Contraseña"
            placeholder="••••••••"
            value={value}
            onChangeText={onChange}
            secureTextEntry
            error={errors.password?.message}
          />
        )}
      />

      <Button
        testID="btn-submit-login"
        title="Ingresar al Sistema"
        onPress={() => handleSubmit(onSubmit)()}
        isLoading={isLoading}
        style={styles.submitBtn}
      />

      {onSwitchToRegister && (
        <Button
          testID="btn-switch-register"
          title="Crear Nueva Empresa (Tenant)"
          variant="secondary"
          onPress={onSwitchToRegister}
          style={styles.registerBtn}
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
  registerBtn: {
    marginTop: 12,
  },
});
