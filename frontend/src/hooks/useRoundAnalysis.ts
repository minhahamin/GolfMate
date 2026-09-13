import { useQuery } from '@tanstack/react-query';

import { getRoundAnalysis } from '../api/rounds';

export function useRoundAnalysis(roundId: number) {
  return useQuery({
    queryKey: ['rounds', roundId, 'analysis'],
    queryFn: () => getRoundAnalysis(roundId),
    enabled: Number.isFinite(roundId),
  });
}
