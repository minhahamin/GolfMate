import { useQuery } from '@tanstack/react-query';

import { getStatisticsSummary } from '../api/rounds';
import { useAuth } from '../context/AuthContext';

export function useStatisticsSummary(limit = 10) {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['rounds', 'statistics', 'summary', limit],
    queryFn: () => getStatisticsSummary(limit),
    enabled: !!user,
  });
}
