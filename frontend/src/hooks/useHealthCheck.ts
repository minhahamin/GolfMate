import { useQuery } from '@tanstack/react-query';

import { apiClient } from '../api/client';
import type { HealthStatus } from '../types/health';

async function fetchDbHealth(): Promise<HealthStatus> {
  const { data } = await apiClient.get<HealthStatus>('/api/health/db');
  return data;
}

/** 백엔드 + DB 연결 상태를 주기적으로 확인한다 (Phase 1 연결 확인용). */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health', 'db'],
    queryFn: fetchDbHealth,
    retry: 1,
    refetchInterval: 10_000,
  });
}
