import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../auth/model/authStore';
import { diningKeys } from './diningApi';

export interface RealtimeMealEvent {
  aggregate_id: string;
  badge_code: string;
  meal_type: string;
  consumed_at: string;
  employee_id: string;
  tenant_id: string;
}

export interface WebSocketMessage {
  type: string;
  data: RealtimeMealEvent;
}

export function useDiningWebSocket() {
  const queryClient = useQueryClient();
  const token = useAuthStore((state) => state.token);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastLiveScan, setLastLiveScan] = useState<RealtimeMealEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!token) return;

    const baseHttp = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
    const baseWs = process.env.EXPO_PUBLIC_WS_URL || baseHttp.replace(/^http/, 'ws');
    const wsUrl = `${baseWs}/dining/ws?token=${encodeURIComponent(token)}`;

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          if (message.type === 'MEAL_RECORDED') {
            setLastLiveScan(message.data);
            // Immediately invalidate dining metrics query to refresh charts & count cards
            queryClient.invalidateQueries({ queryKey: diningKeys.metrics() });
          }
        } catch {
          // ignore non-json or heartbeat frames
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        // Exponential/staggered reconnect attempt if token still active
        reconnectTimeoutRef.current = setTimeout(() => {
          if (token) {
            connect();
          }
        }, 3000);
      };

      socket.onerror = () => {
        socket.close();
      };
    } catch {
      setIsConnected(false);
    }
  }, [token, queryClient]);

  useEffect(() => {
    if (token) {
      connect();
    } else {
      if (wsRef.current) {
        wsRef.current.close();
      }
      setIsConnected(false);
      setLastLiveScan(null);
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token, connect]);

  const clearLastLiveScan = useCallback(() => {
    setLastLiveScan(null);
  }, []);

  return {
    isConnected,
    lastLiveScan,
    clearLastLiveScan,
  };
}
