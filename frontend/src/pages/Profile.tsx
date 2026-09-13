import { useEffect, useState, type FormEvent } from 'react';

import Layout from '../components/Layout';
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

export default function Profile() {
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
    <Layout>
      <h1 className="font-display text-3xl text-ink">골퍼 프로필</h1>
      <p className="mt-1 text-sm text-ink-soft">
        라운드를 기록하면 이 지표들이 자동으로 갱신됩니다. 그 전까지는 직접 입력해두면 AI
        코치/캐디가 참고할 초기값으로 쓰입니다.
      </p>

      <section className="mt-6 border border-ink/15 p-6">
        {isLoading ? (
          <p className="text-sm text-ink-soft">불러오는 중...</p>
        ) : (
          <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {PROFILE_FIELDS.map(({ key, label, step }) => (
              <label key={key} className="text-sm text-ink-soft">
                {label}
                <input
                  type="number"
                  step={step}
                  value={form[key] ?? ''}
                  onChange={(e) => handleChange(key, e.target.value)}
                  className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 font-mono text-ink outline-none focus:border-ink"
                />
              </label>
            ))}

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={updateProfile.isPending}
                className="w-full bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50 sm:w-auto"
              >
                {updateProfile.isPending ? '저장 중...' : '저장'}
              </button>
              {updateProfile.isSuccess && (
                <span className="ml-3 text-sm text-fairway">저장됐습니다.</span>
              )}
            </div>
          </form>
        )}
      </section>
    </Layout>
  );
}
