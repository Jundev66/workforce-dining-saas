import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './src/features/auth/model/authStore';
import { LoginForm } from './src/features/auth/ui/LoginForm';
import { RegisterTenantForm } from './src/features/auth/ui/RegisterTenantForm';
import { EmployeeList } from './src/features/employees/ui/EmployeeList';
import { CreateEmployeeModal } from './src/features/employees/ui/CreateEmployeeModal';
import { EmployeeDetailModal } from './src/features/employees/ui/EmployeeDetailModal';
import { Employee } from './src/features/employees/model/employeeTypes';
import { colors } from './src/shared/theme/colors';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 30,
    },
  },
});

function MainScreen() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.authContainer} testID="auth-screen">
        <View style={styles.authContent}>
          {authView === 'login' ? (
            <LoginForm onSwitchToRegister={() => setAuthView('register')} />
          ) : (
            <RegisterTenantForm onSwitchToLogin={() => setAuthView('login')} />
          )}
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.appContainer} testID="dashboard-screen">
      <View style={styles.navbar}>
        <View>
          <Text style={styles.navLogo}>Staff & Dining SaaS</Text>
          <Text style={styles.navUser}>
            {user?.fullName} ({user?.role})
          </Text>
        </View>

        <View style={styles.navActions}>
          <TouchableOpacity
            testID="btn-open-create-employee"
            style={styles.createBtn}
            onPress={() => setIsCreateOpen(true)}
          >
            <Text style={styles.createBtnText}>+ Nuevo Empleado</Text>
          </TouchableOpacity>

          <TouchableOpacity
            testID="btn-logout"
            style={styles.logoutBtn}
            onPress={logout}
          >
            <Text style={styles.logoutBtnText}>Salir</Text>
          </TouchableOpacity>
        </View>
      </View>

      <EmployeeList onSelectEmployee={(emp) => setSelectedEmployee(emp)} />

      <CreateEmployeeModal
        visible={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
      />

      <EmployeeDetailModal
        employee={selectedEmployee}
        visible={!!selectedEmployee}
        onClose={() => setSelectedEmployee(null)}
      />
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar barStyle="dark-content" />
      <MainScreen />
    </QueryClientProvider>
  );
}

const styles = StyleSheet.create({
  authContainer: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  authContent: {
    width: '100%',
    maxWidth: 440,
  },
  appContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  navbar: {
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  navLogo: {
    fontSize: 17,
    fontWeight: '700',
    color: colors.primary,
  },
  navUser: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
  },
  navActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  createBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  createBtnText: {
    color: colors.textInverse,
    fontSize: 13,
    fontWeight: '600',
  },
  logoutBtn: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: colors.border,
  },
  logoutBtnText: {
    color: colors.textMuted,
    fontSize: 13,
    fontWeight: '500',
  },
});
