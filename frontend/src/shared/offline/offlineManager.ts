import { Platform } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import { onlineManager, QueryClient } from '@tanstack/react-query';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { useState, useEffect } from 'react';

/**
 * Connects TanStack Query's onlineManager to native network status listeners.
 * Ensures queries and mutations pause and resume automatically based on real network reachability.
 */
export function initOnlineManager(): void {
  onlineManager.setEventListener((setOnline) => {
    if (Platform.OS !== 'web') {
      return NetInfo.addEventListener((state) => {
        setOnline(Boolean(state.isConnected && state.isInternetReachable !== false));
      });
    }

    if (typeof window !== 'undefined' && window.addEventListener) {
      const onlineHandler = () => setOnline(true);
      const offlineHandler = () => setOnline(false);

      window.addEventListener('online', onlineHandler);
      window.addEventListener('offline', offlineHandler);

      return () => {
        window.removeEventListener('online', onlineHandler);
        window.removeEventListener('offline', offlineHandler);
      };
    }

    return () => {};
  });
}

/**
 * Creates and configures the offline-first QueryClient with AsyncStorage persistence.
 */
export function createOfflineQueryClient(): QueryClient {
  const client = new QueryClient({
    defaultOptions: {
      queries: {
        networkMode: 'offlineFirst',
        staleTime: 1000 * 60 * 5, // 5 minutes fresh
        gcTime: 1000 * 60 * 60 * 24, // Keep offline cache for 24 hours
        retry: 2,
      },
      mutations: {
        networkMode: 'offlineFirst',
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
    },
  });

  const asyncStoragePersister = createAsyncStoragePersister({
    storage: AsyncStorage,
    throttleTime: 1000,
  });

  persistQueryClient({
    queryClient: client,
    persister: asyncStoragePersister,
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
    buster: 'v2.0-workforce',
  });

  return client;
}

/**
 * Custom React Hook to expose real-time connectivity state in the UI.
 */
export function useIsOnline(): boolean {
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    if (Platform.OS !== 'web') {
      const unsubscribe = NetInfo.addEventListener((state) => {
        setIsOnline(Boolean(state.isConnected && state.isInternetReachable !== false));
      });
      return () => unsubscribe();
    }

    if (typeof window !== 'undefined' && window.addEventListener) {
      const handleOnline = () => setIsOnline(true);
      const handleOffline = () => setIsOnline(false);

      setIsOnline(navigator.onLine);

      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, []);

  return isOnline;
}
