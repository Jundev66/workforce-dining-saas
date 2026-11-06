import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './src/features/auth/model/authStore';
import { LoginForm } from './src/features/auth/ui/LoginForm';
import { RegisterTenantForm } from './src/features/auth/ui/RegisterTenantForm';
import { EmployeeList } from './src/features/employees/ui/EmployeeList';
import { CreateEmployeeModal } from './src/features/employees/ui/CreateEmployeeModal';
import { EmployeeDetailModal } from './src/features/employees/ui/EmployeeDetailModal';
import { ConflictResolutionModal } from './src/features/employees/ui/ConflictResolutionModal';
import { DiningDashboard } from './src/features/dining/ui/DiningDashboard';
import { CopilotScreen } from './src/features/copilot/ui/CopilotScreen';
import { Employee } from './src/features/employees/model/employeeTypes';
import { colors } from './src/shared/theme/colors';
import { initOnlineManager, createOfflineQueryClient } from './src/shared/offline/offlineManager';
import { OfflineBanner } from './src/shared/components/OfflineBanner';

// Initialize network reachability listeners
initOnlineManager();

// Create resilient offline-first QueryClient with AsyncStorage persistence
const queryClient = createOfflineQueryClient();

function MainScreen() {
  const { isAuthenticated, isHydrated, hydrateSession, user, logout } = useAuthStore();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState<'workforce' | 'dining' | 'copilot'>('workforce');
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
        <OfflineBanner />
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
      <OfflineBanner />
      {/* Navigation Header */}
      <View style={styles.navbarWrapper}>
        <View style={styles.navbar}>
          <View style={styles.navBrandCol}>
            <Text style={styles.navLogo} numberOfLines={1}>Staff & Dining SaaS</Text>
            <Text style={styles.navUser} numberOfLines={1}>
              {user?.fullName || 'Usuario'} · {user?.role ? user.role.toUpperCase() : 'ADMIN'}
            </Text>
          </View>

          <View style={styles.navActions}>
            <TouchableOpacity
              testID="btn-logout"
              style={styles.logoutBtn}
              onPress={() => logout()}
            >
              <Text style={styles.logoutBtnText}>Salir</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Main Content Area (Responsive Wrapper) */}
      <View style={styles.mainContentContainer}>
        {activeTab === 'workforce' && (
          <>
            <EmployeeList onSelectEmployee={(emp) => setSelectedEmployee(emp)} />
            <TouchableOpacity
              testID="btn-open-create-employee"
              style={styles.fab}
              activeOpacity={0.85}
              onPress={() => setIsCreateOpen(true)}
            >
              <Text style={styles.fabIcon}>＋</Text>
              <Text style={styles.fabText}>Nuevo</Text>
            </TouchableOpacity>
          </>
        )}
        {activeTab === 'dining' && <DiningDashboard />}
        {activeTab === 'copilot' && <CopilotScreen />}
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.tabBarWrapper}>
        <View style={styles.tabBar}>
          <TouchableOpacity
            testID="tab-workforce"
            style={[styles.tabItem, activeTab === 'workforce' && styles.tabItemActive]}
            onPress={() => setActiveTab('workforce')}
          >
            <Text style={styles.tabIcon}>👥</Text>
            <Text
              numberOfLines={1}
              style={[
                styles.tabText,
                activeTab === 'workforce' && styles.tabTextActive,
              ]}
            >
              Personal
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            testID="tab-dining"
            style={[styles.tabItem, activeTab === 'dining' && styles.tabItemActive]}
            onPress={() => setActiveTab('dining')}
          >
            <Text style={styles.tabIcon}>🍽️</Text>
            <Text
              numberOfLines={1}
              style={[
                styles.tabText,
                activeTab === 'dining' && styles.tabTextActive,
              ]}
            >
              Comedor
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            testID="tab-copilot"
            style={[styles.tabItem, activeTab === 'copilot' && styles.tabItemActive]}
            onPress={() => setActiveTab('copilot')}
          >
            <Text style={styles.tabIcon}>🤖</Text>
            <Text
              numberOfLines={1}
              style={[
                styles.tabText,
                activeTab === 'copilot' && styles.tabTextActive,
              ]}
            >
              Copilot IA
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Workforce Modals */}
      <CreateEmployeeModal
        visible={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
      />

      <EmployeeDetailModal
        employee={selectedEmployee}
        visible={
          !!selectedEmployee &&
          !selectedEmployee.id.startsWith('temp-') &&
          (!selectedEmployee.sync_status || selectedEmployee.sync_status === 'SYNCED')
        }
        onClose={() => setSelectedEmployee(null)}
      />

      <ConflictResolutionModal
        employee={selectedEmployee}
        visible={
          Boolean(
            selectedEmployee &&
              (selectedEmployee.id.startsWith('temp-') ||
                (selectedEmployee.sync_status && selectedEmployee.sync_status !== 'SYNCED'))
          )
        }
        onClose={() => setSelectedEmployee(null)}
        onResolved={() => setSelectedEmployee(null)}
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
    paddingTop: Platform.OS === 'android' ? (StatusBar.currentHeight || 28) + 12 : 16,
  },
  authContent: {
    width: '100%',
    maxWidth: 440,
  },
  appContainer: {
    flex: 1,
    backgroundColor: colors.background,
    paddingTop: Platform.OS === 'android' ? 48 : 0,
  },
  navbarWrapper: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    width: '100%',
  },
  navbar: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: 960,
    width: '100%',
    alignSelf: 'center',
  },
  navBrandCol: {
    flex: 1,
    marginRight: 12,
  },
  navLogo: {
    fontSize: 17,
    fontWeight: '800',
    color: colors.primary,
    letterSpacing: -0.3,
  },
  navUser: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2,
    fontWeight: '500',
  },
  navActions: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: Platform.OS === 'android' ? 52 : 0,
  },
  logoutBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
  },
  logoutBtnText: {
    color: '#475569',
    fontSize: 12,
    fontWeight: '600',
  },
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 20,
    backgroundColor: colors.primary,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 28,
    elevation: 8,
    shadowColor: colors.primary,
    shadowOpacity: 0.35,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    zIndex: 99,
  },
  fabIcon: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
    marginRight: 6,
    lineHeight: 18,
  },
  fabText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  tabBarWrapper: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: colors.border,
    width: '100%',
    paddingBottom: Platform.OS === 'android' ? 22 : 28,
    paddingTop: 8,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: -3 },
    elevation: 10,
  },
  tabBar: {
    flexDirection: 'row',
    maxWidth: 960,
    width: '100%',
    alignSelf: 'center',
  },
  mainContentContainer: {
    flex: 1,
    width: '100%',
    maxWidth: 960,
    alignSelf: 'center',
    backgroundColor: colors.background,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 2,
  },
  tabItemActive: {},
  tabIcon: {
    fontSize: 20,
    marginBottom: 2,
  },
  tabText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#94a3b8',
  },
  tabTextActive: {
    color: colors.primary,
    fontWeight: '700',
  },
});
