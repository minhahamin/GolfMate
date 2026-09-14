import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { createBet, getBet, listBets } from '../api/bets';
import type { BetCreatePayload } from '../types/bet';

export function useBets(groupId: number) {
  return useQuery({
    queryKey: ['groups', groupId, 'bets'],
    queryFn: () => listBets(groupId),
    enabled: Number.isFinite(groupId),
  });
}

export function useBet(betId: number) {
  return useQuery({
    queryKey: ['bets', betId],
    queryFn: () => getBet(betId),
    enabled: Number.isFinite(betId),
  });
}

export function useCreateBet(groupId: number) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: BetCreatePayload) => createBet(groupId, payload),
    onSuccess: (bet) => {
      queryClient.invalidateQueries({ queryKey: ['groups', groupId, 'bets'] });
      navigate(`/bets/${bet.id}`);
    },
  });
}
