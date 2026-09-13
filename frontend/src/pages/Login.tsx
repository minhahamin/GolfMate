import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useLogin } from '../hooks/useLogin';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const loginMutation = useLogin();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    loginMutation.mutate(
      { email, password },
      { onSuccess: () => navigate('/dashboard', { replace: true }) },
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-8 shadow-xl"
      >
        <p className="text-sm uppercase tracking-widest text-emerald-400">GolfMate AI</p>
        <h1 className="mt-1 text-2xl font-semibold text-emerald-50">로그인</h1>

        <label className="mt-6 block text-sm text-emerald-200/80">
          이메일
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
          />
        </label>

        <label className="mt-4 block text-sm text-emerald-200/80">
          비밀번호
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
          />
        </label>

        {loginMutation.isError && (
          <p className="mt-4 text-sm text-red-400">
            이메일 또는 비밀번호가 올바르지 않습니다.
          </p>
        )}

        <button
          type="submit"
          disabled={loginMutation.isPending}
          className="mt-6 w-full rounded-lg bg-emerald-500 py-2 font-medium text-emerald-950 transition hover:bg-emerald-400 disabled:opacity-50"
        >
          {loginMutation.isPending ? '로그인 중...' : '로그인'}
        </button>

        <p className="mt-4 text-center text-sm text-emerald-200/60">
          아직 계정이 없으신가요?{' '}
          <Link to="/register" className="text-emerald-400 hover:underline">
            회원가입
          </Link>
        </p>
      </form>
    </main>
  );
}
