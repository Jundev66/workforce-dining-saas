import React, { useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  RefreshControl,
  ListRenderItem,
} from 'react-native';
import { Employee } from '../model/employeeTypes';
import { useEmployeesQuery } from '../api/employeeApi';
import { useSyncTransactions } from '../../../shared/offline/useSyncLedger';
import { EmployeeCard } from './EmployeeCard';
import { Input } from '../../../shared/components/Input';
import { colors } from '../../../shared/theme/colors';

interface EmployeeListProps {
  onSelectEmployee: (employee: Employee) => void;
}

export const EmployeeList: React.FC<EmployeeListProps> = ({
  onSelectEmployee,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const { transactions } = useSyncTransactions();

  const { data, isLoading, isError, refetch, isRefetching } = useEmployeesQuery({
    search: searchTerm.length >= 2 ? searchTerm : undefined,
  });

  // Filter employee drafts that are not yet confirmed in the backend
  const activeDrafts: Employee[] = useMemo(() => {
    return transactions
      .filter(
        (tx) =>
          tx.entityType === 'employee' &&
          tx.status !== 'SYNCED' &&
          tx.status !== 'DISCARDED'
      )
      .map((tx) => {
        const p = tx.payload || {};
        return {
          id: tx.tempEntityId,
          tenant_id: 'local-draft',
          first_name: p.first_name || '',
          last_name: p.last_name || '',
          full_name:
            `${p.first_name || ''} ${p.last_name || ''}`.trim() ||
            'Empleado Borrador',
          document_id: p.document_id || '',
          department: p.department || 'General',
          position: p.position || 'Operador',
          badge_code: p.badge_code || 'EMP-SYNC',
          status: 'active',
          sync_status: tx.status,
          sync_error: tx.lastError?.message || null,
          sync_transaction_id: tx.id,
        };
      });
  }, [transactions]);

  const serverItems = data?.items || [];

  // Merge drafts with server items, avoiding duplicates
  const employees = useMemo(() => {
    const list = [...activeDrafts];
    for (const item of serverItems) {
      if (
        !list.some(
          (d) =>
            d.id === item.id ||
            (item.document_id && d.document_id === item.document_id)
        )
      ) {
        list.push(item);
      }
    }
    return list;
  }, [activeDrafts, serverItems]);

  const total = (data?.total || 0) + activeDrafts.length;

  const renderItem: ListRenderItem<Employee> = useCallback(
    ({ item }) => (
      <EmployeeCard employee={item} onPress={onSelectEmployee} />
    ),
    [onSelectEmployee]
  );

  const keyExtractor = useCallback((item: Employee) => item.id, []);

  return (
    <View style={styles.container} testID="employee-list-container">
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Nómina de Empleados</Text>
          <Text style={styles.subtitle}>
            {total} registrados {activeDrafts.length > 0 ? `(${activeDrafts.length} en dispositivo)` : ''}
          </Text>
        </View>
      </View>

      <Input
        testID="input-search-employee"
        placeholder="Buscar por nombre, documento o credencial..."
        value={searchTerm}
        onChangeText={setSearchTerm}
        style={styles.searchBar}
      />

      {isLoading && employees.length === 0 ? (
        <View style={styles.centerContainer} testID="loading-employees">
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Cargando nómina...</Text>
        </View>
      ) : isError && employees.length === 0 ? (
        <View style={styles.centerContainer} testID="error-employees">
          <Text style={styles.errorText}>Error al cargar los empleados.</Text>
        </View>
      ) : (
        <FlatList
          testID="flatlist-employees"
          data={employees}
          renderItem={renderItem}
          keyExtractor={keyExtractor}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContent}
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          removeClippedSubviews={true}
          refreshControl={
            <RefreshControl
              refreshing={isRefetching}
              onRefresh={() => {
                refetch();
              }}
              tintColor={colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer} testID="empty-employees">
              <Text style={styles.emptyText}>No se encontraron empleados</Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textMuted,
    marginTop: 2,
  },
  searchBar: {
    marginBottom: 16,
  },
  listContent: {
    paddingBottom: 80,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: colors.textMuted,
  },
  errorText: {
    fontSize: 14,
    color: colors.danger,
  },
  emptyContainer: {
    paddingVertical: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: colors.textMuted,
  },
});
