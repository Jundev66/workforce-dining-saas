import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../shared/api/client';
import { MealScanResult, DiningMetrics, AiForecast } from '../model/diningTypes';

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
      return apiClient<MealScanResult>('/dining/scan', {
        method: 'POST',
        body: JSON.stringify({
          badge_code: payload.badgeCode,
          meal_type: payload.mealType,
          notes: payload.notes,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: diningKeys.metrics() });
    },
  });
};
