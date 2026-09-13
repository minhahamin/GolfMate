import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { createRound, deleteRound, getRound, listRounds, updateRound } from '../api/rounds';

const ROUNDS_KEY = ['rounds'];

export function useRounds() {
  return useQuery({ queryKey: ROUNDS_KEY, queryFn: listRounds });
}

export function useRound(roundId: number) {
  return useQuery({
    queryKey: [...ROUNDS_KEY, roundId],
    queryFn: () => getRound(roundId),
    enabled: Number.isFinite(roundId),
  });
}

export function useCreateRound() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: createRound,
    onSuccess: (round) => {
      queryClient.invalidateQueries({ queryKey: ROUNDS_KEY });
      navigate(`/rounds/${round.id}`);
    },
  });
}

export function useUpdateRound(roundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof updateRound>[1]) => updateRound(roundId, payload),
    onSuccess: (round) => {
      queryClient.setQueryData([...ROUNDS_KEY, roundId], round);
      queryClient.invalidateQueries({ queryKey: ROUNDS_KEY });
    },
  });
}

export function useDeleteRound() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: deleteRound,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ROUNDS_KEY });
      navigate('/rounds');
    },
  });
}
