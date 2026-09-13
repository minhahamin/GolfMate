import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/dashboard', label: '대시보드' },
  { to: '/rounds', label: '라운드' },
  { to: '/courses', label: '골프장' },
  { to: '/profile', label: '프로필' },
];

// 로그인 이후 화면(Dashboard/Rounds/Courses/Profile) 공통 상단 네비게이션.
export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen">
      <header className="border-b border-emerald-800/40 bg-emerald-950/60">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <div className="flex flex-wrap items-center gap-6">
            <span className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
              GolfMate AI
            </span>
            <nav className="flex gap-4 text-sm">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    isActive
                      ? 'font-medium text-emerald-50'
                      : 'text-emerald-200/60 hover:text-emerald-100'
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3 text-sm text-emerald-200/70">
            <span>{user?.name}</span>
            <button
              onClick={logout}
              className="rounded-lg border border-emerald-800/50 px-3 py-1.5 transition hover:bg-emerald-900/40"
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
