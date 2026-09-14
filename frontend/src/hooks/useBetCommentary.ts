import { useMutation } from '@tanstack/react-query';

import { postBetCommentary } from '../api/bets';

export function useBetCommentary() {
  return useMutation({
    mutationFn: (betId: number) => postBetCommentary(betId),
  });
}
