import { useEffect, useState, type FormEvent } from 'react';

import { useAuth } from '../context/AuthContext';
import { useMyProfile, useUpdateMyProfile } from '../hooks/useMyProfile';
import type { GolferProfileUpdate } from '../types/auth';

const PROFILE_FIELDS: { key: keyof GolferProfileUpdate; label: string; step?: string }[] = [
  { key: 'handicap', label: '핸디캡', step: '0.1' },
  { key: 'average_score', label: '평균 타수', step: '0.1' },
  { key: 'driver_distance', label: '드라이버 평균 거리 (m)', step: '1' },
  { key: 'iron_distance', label: '아이언 평균 거리 (m)', step: '1' },
  { key: 'putting_average', label: '퍼팅 평균', step: '0.1' },
  { key: 'fairway_percentage', label: '페어웨이 적중률 (%)', step: '0.1' },
  { key: 'gir_percentage', label: 'GIR (%)', step: '0.1' },
  { key: 'goal_score', label: '목표 타수', step: '1' },
];

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { data: profile, isLoading } = useMyProfile();
  const updateProfile = useUpdateMyProfile();

  const [form, setForm] = useState<GolferProfileUpdate>({});

  useEffect(() => {
    if (profile) {
      setForm(profile);
    }
  }, [profile]);

  function handleChange(key: keyof GolferProfileUpdate, value: string) {
    setForm((prev) => ({ ...prev, [key]: value === '' ? null : Number(value) }));
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    updateProfile.mutate(form);
  }

  return (
    <main className="min-h-screen px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-widest text-emerald-400">GolfMate AI</p>
            <h1 className="mt-1 text-2xl font-semibold text-emerald-50">
              {user?.name}님, 안녕하세요
            </h1>
            <p className="mt-1 text-sm text-emerald-200/60">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="h-fit rounded-lg border border-emerald-800/50 px-4 py-2 text-sm text-emerald-200 transition hover:bg-emerald-900/40"
          >
            로그아웃
          </button>
        </div>

        <section className="mt-8 rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6 shadow-xl">
          <h2 className="text-lg font-medium text-emerald-50">골퍼 프로필</h2>
          <p className="mt-1 text-sm text-emerald-200/60">
            아직 라운드 데이터가 없어 직접 입력한 값입니다. Phase 3부터는 라운드 기록에서
            자동으로 계산됩니다.
          </p>

          {isLoading ? (
            <p className="mt-6 text-sm text-emerald-200/60">불러오는 중...</p>
          ) : (
            <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {PROFILE_FIELDS.map(({ key, label, step }) => (
                <label key={key} className="text-sm text-emerald-200/80">
                  {label}
                  <input
                    type="number"
                    step={step}
                    value={form[key] ?? ''}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
                  />
                </label>
              ))}

              <div className="sm:col-span-2">
                <button
                  type="submit"
                  disabled={updateProfile.isPending}
                  className="w-full rounded-lg bg-emerald-500 py-2 font-medium text-emerald-950 transition hover:bg-emerald-400 disabled:opacity-50 sm:w-auto sm:px-6"
                >
                  {updateProfile.isPending ? '저장 중...' : '저장'}
                </button>
                {updateProfile.isSuccess && (
                  <span className="ml-3 text-sm text-emerald-400">저장됐습니다.</span>
                )}
              </div>
            </form>
          )}
        </section>
      </div>
    </main>
  );
}
