import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, ApiError } from '../../../shared/api/client';
import { MealScanResult, DiningMetrics, AiForecast } from '../model/diningTypes';
import { syncLedger } from '../../../shared/offline/syncLedger';

export const diningKeys = {
  all: ['dining'] as const,
  metrics: () => [...diningKeys.all, 'metrics'] as const,
  forecast: () => [...diningKeys.all, 'forecast'] as const,
};

export const useDiningMetricsQuery = () => {
  return useQuery<DiningMetrics>({
    queryKey: diningKeys.metrics(),
    queryFn: () => apiClient<DiningMetrics>('/dining/metrics/today'),
    refetchInterval: 1000 * 15, // poll every 15s in the dining hall dashboard
  });
};

export const useAiForecastQuery = () => {
  return useQuery<AiForecast>({
    queryKey: diningKeys.forecast(),
    queryFn: () => apiClient<AiForecast>('/dining/ai/forecast'),
    staleTime: 1000 * 60 * 5, // 5 min cache
  });
};

export const useScanMealMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { badgeCode: string; mealType: string; notes?: string }) => {
      const tempId = `temp-meal-${Date.now()}`;

      // Enqueue to Outbox Ledger (SSOT)
      const tx = await syncLedger.enqueue({
        entityType: 'dining_scan',
        tempEntityId: tempId,
        action: 'CREATE',
        endpoint: '/dining/scan',
        httpMethod: 'POST',
        payload: {
          badge_code: payload.badgeCode,
          meal_type: payload.mealType,
          notes: payload.notes,
        },
        autoProcess: false,
      });

      try {
        const result = await syncLedger.executeTransaction(tx);
        return result;
      } catch (err: any) {
        // Business rule rejection (e.g. HTTP 409 duplicate scan) is thrown immediately
        if (err instanceof ApiError && (err.status === 400 || err.status === 409 || err.status === 422)) {
          throw err;
        }

        // If network failure / offline, preserve optimistic attendance in local outbox
        return {
          id: tempId,
          status: 'pending_sync',
          approved: true,
          employee_id: 'pending-sync',
          employee_name: `Borrador Offline (${payload.badgeCode})`,
          department: 'Comedor',
          meal_type: payload.mealType,
          badge_code: payload.badgeCode,
          message: '✓ Registrado en cola offline. Se sincronizará al recuperar la conexión.',
          consumed_at: new Date().toISOString(),
        } as MealScanResult;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: diningKeys.metrics() });
    },
  });
};
