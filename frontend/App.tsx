import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './src/features/auth/model/authStore';
import { LoginForm } from './src/features/auth/ui/LoginForm';
import { RegisterTenantForm } from './src/features/auth/ui/RegisterTenantForm';
import { EmployeeList } from './src/features/employees/ui/EmployeeList';
import { CreateEmployeeModal } from './src/features/employees/ui/CreateEmployeeModal';
import { EmployeeDetailModal } from './src/features/employees/ui/EmployeeDetailModal';
import { DiningDashboard } from './src/features/dining/ui/DiningDashboard';
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
  const { isAuthenticated, isHydrated, hydrateSession, user, logout } = useAuthStore();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState<'workforce' | 'dining'>('workforce');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  useEffect(() => {
    hydrateSession();
  }, [hydrateSession]);

  if (!isHydrated) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

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
      {/* Navigation Header */}
      <View style={styles.navbar}>
        <View>
          <Text style={styles.navLogo}>Staff & Dining SaaS</Text>
          <Text style={styles.navUser}>
            {user?.fullName} ({user?.role})
          </Text>
        </View>

        <View style={styles.navActions}>
          {activeTab === 'workforce' && (
            <TouchableOpacity
              testID="btn-open-create-employee"
              style={styles.createBtn}
              onPress={() => setIsCreateOpen(true)}
            >
              <Text style={styles.createBtnText}>+ Nuevo Empleado</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            testID="btn-logout"
            style={styles.logoutBtn}
            onPress={() => logout()}
          >
            <Text style={styles.logoutBtnText}>Salir</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Module Tabs (Workforce vs Dining) */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          testID="tab-workforce"
          style={[styles.tabItem, activeTab === 'workforce' && styles.tabItemActive]}
          onPress={() => setActiveTab('workforce')}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === 'workforce' && styles.tabTextActive,
            ]}
          >
            👥 Gestión de Personal
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          testID="tab-dining"
          style={[styles.tabItem, activeTab === 'dining' && styles.tabItemActive]}
          onPress={() => setActiveTab('dining')}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === 'dining' && styles.tabTextActive,
            ]}
          >
            🍽️ Comedor & IA
          </Text>
        </TouchableOpacity>
      </View>

      {/* Main Content Area */}
      {activeTab === 'workforce' ? (
        <EmployeeList onSelectEmployee={(emp) => setSelectedEmployee(emp)} />
      ) : (
        <DiningDashboard />
      )}

      {/* Workforce Modals */}
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
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
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tabItem: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabItemActive: {
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textMuted,
  },
  tabTextActive: {
    color: colors.primary,
  },
});
