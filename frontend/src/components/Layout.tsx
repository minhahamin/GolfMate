import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/dashboard', label: '대시보드' },
  { to: '/coach', label: 'AI 코치' },
  { to: '/diary', label: 'AI 일기' },
  { to: '/rounds', label: '라운드' },
  { to: '/courses', label: '골프장' },
  { to: '/profile', label: '프로필' },
];

function FlagMark() {
  return (
    <svg width="16" height="20" viewBox="0 0 16 20" fill="none" aria-hidden="true">
      <path d="M2 19V1" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M2 2L13 5.5L2 9V2Z" fill="var(--flag)" stroke="currentColor" strokeWidth="1" />
    </svg>
  );
}

// 로그인 이후 화면(Dashboard/Coach/Rounds/Courses/Profile) 공통 상단 네비게이션.
export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-ink/15">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <div className="flex flex-wrap items-center gap-8">
            <span className="flex items-center gap-2 font-display text-lg text-ink">
              <span className="text-ink">
                <FlagMark />
              </span>
              GolfMate
            </span>
            <nav className="flex gap-5 text-sm">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    isActive
                      ? 'border-b-2 border-flag pb-0.5 font-medium text-ink'
                      : 'pb-0.5 text-ink-soft transition hover:text-ink'
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3 text-sm text-ink-soft">
            <span>{user?.name}</span>
            <button
              onClick={logout}
              className="rounded border border-ink/20 px-3 py-1.5 text-ink transition hover:bg-paper-2"
            >
              로그아웃
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
    </div>
  );
}
