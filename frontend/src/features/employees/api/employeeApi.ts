import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../shared/api/client';
import { Employee, PaginatedEmployees } from '../model/employeeTypes';
import { EmployeeFormData } from '../model/employeeSchemas';

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
      return apiClient<Employee>('/employees', {
        method: 'POST',
        body: JSON.stringify({
          first_name: data.firstName,
          last_name: data.lastName,
          document_id: data.documentId,
          department: data.department,
          position: data.position,
          email: data.email || null,
          phone: data.phone || null,
          badge_code: data.badgeCode || null,
        }),
      });
    },
    onMutate: async (newEmployeeData: EmployeeFormData) => {
      await queryClient.cancelQueries({ queryKey: employeeKeys.lists() });
      const previousQueries = queryClient.getQueriesData<PaginatedEmployees>({ queryKey: employeeKeys.lists() });

      const optimisticEmployee: Employee = {
        id: `temp-${Date.now()}`,
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

      return { previousQueries };
    },
    onError: (_err, _variables, context) => {
      if (context?.previousQueries) {
        context.previousQueries.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
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
