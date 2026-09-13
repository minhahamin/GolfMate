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
    <main className="flex min-h-screen bg-paper">
      <AuthHero tagline="가입하고 나만의 라운드 기록을 쌓아보세요." />

      <div className="flex flex-1 items-center justify-center px-4 py-10">
        <form onSubmit={handleSubmit} className="w-full max-w-sm">
          <h1 className="font-display text-3xl text-ink">회원가입</h1>
          <p className="mt-2 text-sm text-ink-soft">첫 라운드부터 기록을 쌓아보세요.</p>

          <label className="mt-8 block text-sm text-ink-soft">
            이름
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink"
            />
          </label>

          <label className="mt-4 block text-sm text-ink-soft">
            이메일
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink"
            />
          </label>

          <label className="mt-4 block text-sm text-ink-soft">
            비밀번호 (8자 이상)
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink"
            />
          </label>

          {errorMessage && <p className="mt-4 text-sm text-flag">{errorMessage}</p>}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            className="mt-6 w-full bg-flag py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
          >
            {registerMutation.isPending ? '가입 중...' : '회원가입'}
          </button>

          <p className="mt-6 text-sm text-ink-soft">
            이미 계정이 있으신가요?{' '}
            <Link to="/login" className="text-ink underline underline-offset-2">
              로그인
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
