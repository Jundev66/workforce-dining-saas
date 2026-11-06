import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, ApiError } from '../../../shared/api/client';
import { Employee, PaginatedEmployees } from '../model/employeeTypes';
import { EmployeeFormData } from '../model/employeeSchemas';
import { syncLedger } from '../../../shared/offline/syncLedger';

export const employeeKeys = {
  all: ['employees'] as const,
  lists: () => [...employeeKeys.all, 'list'] as const,
  list: (filters: { skip?: number; limit?: number; search?: string; status?: string }) =>
    [...employeeKeys.lists(), filters] as const,
  details: () => [...employeeKeys.all, 'detail'] as const,
  detail: (id: string) => [...employeeKeys.details(), id] as const,
};

export const useEmployeesQuery = (filters: {
  skip?: number;
  limit?: number;
  search?: string;
  status?: string;
  enabled?: boolean;
}) => {
  const { skip = 0, limit = 20, search, status, enabled = true } = filters;

  return useQuery<PaginatedEmployees>({
    queryKey: employeeKeys.list({ skip, limit, search, status }),
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('skip', skip.toString());
      params.append('limit', limit.toString());
      if (search) params.append('search', search);
      if (status) params.append('status', status);

      return apiClient<PaginatedEmployees>(`/employees?${params.toString()}`);
    },
    enabled,
    staleTime: 1000 * 60, // 1 minute cache
  });
};

export const useEmployeeDetailQuery = (employeeId: string, enabled = true) => {
  return useQuery<Employee>({
    queryKey: employeeKeys.detail(employeeId),
    queryFn: () => apiClient<Employee>(`/employees/${employeeId}`),
    enabled: enabled && !!employeeId,
  });
};

export const useCreateEmployeeMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['createEmployee'],
    mutationFn: async (data: EmployeeFormData) => {
      const tempId = `temp-${Date.now()}`;
      const payload = {
        first_name: data.firstName,
        last_name: data.lastName,
        document_id: data.documentId,
        department: data.department,
        position: data.position,
        email: data.email || null,
        phone: data.phone || null,
        badge_code: data.badgeCode || null,
      };

      // Register transaction in the persistent Outbox Ledger (SSOT)
      const tx = await syncLedger.enqueue({
        entityType: 'employee',
        tempEntityId: tempId,
        action: 'CREATE',
        endpoint: '/employees',
        httpMethod: 'POST',
        payload,
        autoProcess: false, // Prevents background double-dispatch while this mutation runs
      });

      // Execute via the SSOT Outbox with stable X-Idempotency-Key
      try {
        const result = await syncLedger.executeTransaction(tx);
        return {
          ...result,
          _tempId: tempId,
          _txId: tx.id,
        };
      } catch (err) {
        throw err;
      }
    },
    onMutate: async (newEmployeeData: EmployeeFormData) => {
      await queryClient.cancelQueries({ queryKey: employeeKeys.lists() });
      const previousQueries = queryClient.getQueriesData<PaginatedEmployees>({ queryKey: employeeKeys.lists() });

      const tempId = `temp-${Date.now()}`;
      const optimisticEmployee: Employee = {
        id: tempId,
        tenant_id: 'pending-sync',
        first_name: newEmployeeData.firstName,
        last_name: newEmployeeData.lastName,
        full_name: `${newEmployeeData.firstName} ${newEmployeeData.lastName}`.trim(),
        document_id: newEmployeeData.documentId,
        department: newEmployeeData.department,
        position: newEmployeeData.position,
        badge_code: newEmployeeData.badgeCode || 'EMP-SYNC',
        email: newEmployeeData.email || null,
        phone: newEmployeeData.phone || null,
        status: 'active',
        sync_status: 'PENDING',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueriesData<PaginatedEmployees>({ queryKey: employeeKeys.lists() }, (old) => {
        if (!old) return old;
        return {
          ...old,
          total: old.total + 1,
          items: [optimisticEmployee, ...old.items],
        };
      });

      return { previousQueries, tempId };
    },
    onError: (err: any, _variables, context) => {
      // NON-DESTRUCTIVE ROLLBACK:
      // If it's a conflict or business rule failure (400, 409, 422), do NOT wipe local state!
      const status = err instanceof ApiError ? err.status : err?.status || 0;
      const message = err.message || 'Error al sincronizar empleado';

      if (context?.tempId) {
        queryClient.setQueriesData<PaginatedEmployees>({ queryKey: employeeKeys.lists() }, (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((emp) => {
              if (emp.id === context.tempId) {
                return {
                  ...emp,
                  sync_status: (status === 409 || status === 422 || status === 400)
                    ? 'CONFLICT_ACTION_REQUIRED'
                    : 'FAILED_RETRYABLE',
                  sync_error: message,
                };
              }
              return emp;
            }),
          };
        });
      }
    },
    onSuccess: (savedEmployee: any, _variables, context) => {
      const targetTempId = savedEmployee?._tempId || context?.tempId;
      if (targetTempId) {
        queryClient.setQueriesData<PaginatedEmployees>({ queryKey: employeeKeys.lists() }, (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((emp) => {
              if (emp.id === targetTempId) {
                return {
                  ...savedEmployee,
                  sync_status: 'SYNCED',
                  sync_transaction_id: savedEmployee?._txId,
                };
              }
              return emp;
            }),
          };
        });
      }
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};

export const useUpdateEmployeeMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['updateEmployee'],
    mutationFn: async ({ id, data }: { id: string; data: Partial<EmployeeFormData> & { status?: string } }) => {
      return apiClient<Employee>(`/employees/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
          first_name: data.firstName,
          last_name: data.lastName,
          department: data.department,
          position: data.position,
          email: data.email || null,
          phone: data.phone || null,
          status: data.status,
        }),
      });
    },
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: employeeKeys.detail(id) });
      const previousDetail = queryClient.getQueryData<Employee>(employeeKeys.detail(id));

      if (previousDetail) {
        queryClient.setQueryData<Employee>(employeeKeys.detail(id), {
          ...previousDetail,
          status: (data.status as any) || previousDetail.status,
          first_name: data.firstName || previousDetail.first_name,
          last_name: data.lastName || previousDetail.last_name,
          department: data.department || previousDetail.department,
          position: data.position || previousDetail.position,
        });
      }

      return { previousDetail };
    },
    onError: (_err, { id }, context) => {
      if (context?.previousDetail) {
        queryClient.setQueryData(employeeKeys.detail(id), context.previousDetail);
      }
    },
    onSettled: (updated, _err, { id }) => {
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
      const targetId = updated?.id || id;
      if (targetId) {
        queryClient.invalidateQueries({ queryKey: employeeKeys.detail(targetId) });
      }
    },
  });
};

export const useDeleteEmployeeMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      return apiClient<void>(`/employees/${id}`, {
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
    },
  });
};
