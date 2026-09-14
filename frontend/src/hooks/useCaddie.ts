import { useMutation } from '@tanstack/react-query';

import { postCaddieAdvice } from '../api/caddie';
import type { CaddieRequest } from '../types/caddie';

export function useCaddie() {
  return useMutation({
    mutationFn: (payload: CaddieRequest) => postCaddieAdvice(payload),
  });
}
