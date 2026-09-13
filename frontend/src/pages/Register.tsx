import { isAxiosError } from 'axios';
import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import AuthHero from '../components/AuthHero';
import { useRegister } from '../hooks/useRegister';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const navigate = useNavigate();
  const registerMutation = useRegister();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    registerMutation.mutate(
      { email, password, name },
      { onSuccess: () => navigate('/dashboard', { replace: true }) },
    );
  }

  const errorMessage = registerMutation.isError
    ? isAxiosError(registerMutation.error) && registerMutation.error.response?.status === 409
      ? '이미 가입된 이메일입니다.'
      : '회원가입에 실패했습니다. 입력값을 확인해주세요.'
    : null;

  return (
    <main className="flex min-h-screen">
      <AuthHero tagline="가입하고 나만의 라운드 기록을 쌓아보세요." />

      <div className="flex flex-1 items-center justify-center px-4 py-10">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-sm rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-8 shadow-xl"
        >
          <p className="text-sm uppercase tracking-widest text-emerald-400">GolfMate AI</p>
          <h1 className="mt-1 text-2xl font-semibold text-emerald-50">회원가입</h1>

          <label className="mt-6 block text-sm text-emerald-200/80">
            이름
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            />
          </label>

          <label className="mt-4 block text-sm text-emerald-200/80">
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
            비밀번호 (8자 이상)
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            />
          </label>

          {errorMessage && <p className="mt-4 text-sm text-red-400">{errorMessage}</p>}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            className="mt-6 w-full rounded-lg bg-emerald-500 py-2 font-medium text-emerald-950 transition hover:bg-emerald-400 disabled:opacity-50"
          >
            {registerMutation.isPending ? '가입 중...' : '회원가입'}
          </button>

          <p className="mt-4 text-center text-sm text-emerald-200/60">
            이미 계정이 있으신가요?{' '}
            <Link to="/login" className="text-emerald-400 hover:underline">
              로그인
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
