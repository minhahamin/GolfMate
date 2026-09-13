import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import AuthHero from '../components/AuthHero';
import { useLogin } from '../hooks/useLogin';

// 포트폴리오 방문자가 가입 없이 바로 체험할 수 있는 데모 계정 (backend/app/seed_demo_account.py로 생성됨).
const DEMO_CREDENTIALS = { email: 'demo@golfmate.ai', password: 'golfmate-demo!' };

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

  function handleDemoLogin() {
    loginMutation.mutate(DEMO_CREDENTIALS, {
      onSuccess: () => navigate('/dashboard', { replace: true }),
    });
  }

  return (
    <main className="flex min-h-screen bg-paper">
      <AuthHero tagline="캐디 토끼가 매 홀 전략을 알려드려요." />

      <div className="flex flex-1 items-center justify-center px-4 py-10">
        <form onSubmit={handleSubmit} className="w-full max-w-sm">
          <h1 className="font-display text-3xl text-ink">로그인</h1>
          <p className="mt-2 text-sm text-ink-soft">GolfMate 계정으로 이어서 기록하세요.</p>

          <label className="mt-8 block text-sm text-ink-soft">
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
            비밀번호
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink"
            />
          </label>

          {loginMutation.isError && (
            <p className="mt-4 text-sm text-flag">이메일 또는 비밀번호가 올바르지 않습니다.</p>
          )}

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="mt-6 w-full bg-flag py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
          >
            {loginMutation.isPending ? '로그인 중...' : '로그인'}
          </button>

          <button
            type="button"
            onClick={handleDemoLogin}
            disabled={loginMutation.isPending}
            className="mt-3 w-full border border-ink/20 py-2.5 text-sm font-medium text-ink transition hover:bg-paper-2 disabled:opacity-50"
          >
            데모 계정으로 체험하기
          </button>

          <p className="mt-6 text-sm text-ink-soft">
            아직 계정이 없으신가요?{' '}
            <Link to="/register" className="text-ink underline underline-offset-2">
              회원가입
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
