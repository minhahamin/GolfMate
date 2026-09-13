import { useMutation } from '@tanstack/react-query';

import { postCoachAnalysis } from '../api/coach';

export function useCoach() {
  return useMutation({
    mutationFn: (question: string) => postCoachAnalysis(question),
  });
}
