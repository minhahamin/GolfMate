import { useMutation } from '@tanstack/react-query';

import { register } from '../api/auth';
import { useAuth } from '../context/AuthContext';

export function useRegister() {
  const { loginWithAuthResponse } = useAuth();

  return useMutation({
    mutationFn: register,
    onSuccess: loginWithAuthResponse,
  });
}
