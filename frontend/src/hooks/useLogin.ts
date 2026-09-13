import { useMutation } from '@tanstack/react-query';

import { login } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export function useLogin() {
  const { loginWithAuthResponse } = useAuth();

  return useMutation({
    mutationFn: login,
    onSuccess: loginWithAuthResponse,
  });
}
