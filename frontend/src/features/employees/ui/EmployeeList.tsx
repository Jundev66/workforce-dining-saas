import React, { useState, useCallback } from 'react';
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

  const { data, isLoading, isError, refetch, isRefetching } = useEmployeesQuery({
    search: searchTerm.length >= 2 ? searchTerm : undefined,
  });

  const employees = data?.items || [];
  const total = data?.total || 0;

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
          <Text style={styles.subtitle}>{total} registrados</Text>
        </View>
      </View>

      <Input
        testID="input-search-employee"
        placeholder="Buscar por nombre, documento o credencial..."
        value={searchTerm}
        onChangeText={setSearchTerm}
        style={styles.searchBar}
      />

      {isLoading ? (
        <View style={styles.centerContainer} testID="loading-employees">
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Cargando nómina...</Text>
        </View>
      ) : isError ? (
        <View style={styles.centerContainer} testID="error-employees">
          <Text style={styles.errorText}>Error al cargar los empleados.</Text>
        </View>
      ) : (
        <FlatList
          testID="flatlist-employees"
          data={employees}
          renderItem={renderItem}
          keyExtractor={keyExtractor}
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
              colors={[colors.primary]}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer} testID="empty-employees-notice">
              <Text style={styles.emptyText}>No se encontraron empleados.</Text>
              <Text style={styles.emptySubtext}>
                Registrá tu primer colaborador para comenzar el seguimiento.
              </Text>
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
    padding: 16,
    backgroundColor: colors.background,
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
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 2,
  },
  searchBar: {
    marginBottom: 12,
  },
  listContent: {
    paddingBottom: 24,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: colors.textMuted,
  },
  errorText: {
    color: colors.danger,
    fontSize: 14,
    fontWeight: '500',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  emptySubtext: {
    fontSize: 13,
    color: colors.textMuted,
    textAlign: 'center',
    marginTop: 6,
  },
});
