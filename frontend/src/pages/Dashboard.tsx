import { Link } from 'react-router-dom';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import golferRabbit from '../assets/golfer-rabbit.png';
import Layout from '../components/Layout';
import StatBar from '../components/StatBar';
import { useAuth } from '../context/AuthContext';
import { useMyProfile } from '../hooks/useMyProfile';
import { useStatisticsSummary } from '../hooks/useStatisticsSummary';

function StatCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-4 py-3 first:pl-0 last:pr-0">
      <p className="text-xs text-ink-soft">{label}</p>
      <p className="mt-1 font-mono text-3xl text-ink">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const { data: profile } = useMyProfile();
  const { data: stats, isLoading } = useStatisticsSummary(10);

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">{user?.name}님, 안녕하세요</h1>
      <p className="mt-1 text-sm text-ink-soft">최근 10라운드 기준 통계입니다.</p>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : !stats || stats.rounds_count === 0 ? (
        <div className="mt-8 flex flex-col items-center gap-6 border border-ink/15 bg-paper-2 p-8 sm:flex-row">
          <div className="w-32 shrink-0 overflow-hidden rounded border border-ink/15 shadow-[3px_3px_0_0_var(--ink)]">
            <img src={golferRabbit} alt="골프 캐디 토끼" className="aspect-square w-full object-cover" />
          </div>
          <div>
            <h2 className="font-display text-xl text-ink">아직 기록된 라운드가 없어요</h2>
            <p className="mt-1 text-sm text-ink-soft">
              첫 라운드를 등록하면 평균 스코어, 퍼팅, 페어웨이 적중률 같은 통계가 여기 쌓입니다.
            </p>
            <Link
              to="/rounds/new"
              className="mt-4 inline-block bg-flag px-5 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
            >
              라운드 등록하기
            </Link>
          </div>
        </div>
      ) : (
        <>
          <div className="mt-6 flex flex-wrap divide-x divide-ink/15 border-y border-ink/15">
            <StatCell label="핸디캡" value={profile?.handicap?.toString() ?? '—'} />
            <StatCell label="평균 스코어" value={stats.average_score?.toString() ?? '—'} />
            <StatCell label="베스트 스코어" value={stats.best_score?.toString() ?? '—'} />
            <StatCell label="기록된 라운드" value={`${stats.rounds_count}회`} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <section className="border border-ink/15 p-6">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg text-ink">🤖 AI 분석</h2>
                <Link to="/coach" className="text-xs text-ink underline underline-offset-2">
                  AI 코치에게 물어보기
                </Link>
              </div>
              <p className="mt-1 text-xs text-ink-soft">계산 기반 최근 10라운드 지표입니다.</p>
              <div className="mt-4 space-y-4">
                {stats.average_fairway_rate != null && (
                  <StatBar label="페어웨이 적중률" value={stats.average_fairway_rate} />
                )}
                {stats.average_gir_rate != null && (
                  <StatBar label="GIR" value={stats.average_gir_rate} />
                )}
                {stats.average_putts != null && (
                  <StatBar
                    label="평균 퍼팅 수"
                    value={Math.min((stats.average_putts / 36) * 100, 100)}
                    displayValue={`${stats.average_putts}개`}
                  />
                )}
              </div>
            </section>

            <section className="border border-ink/15 p-6">
              <h2 className="font-display text-lg text-ink">스코어 추이</h2>
              <div className="mt-4 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats.recent_rounds}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ebe8da" />
                    <XAxis dataKey="round_date" tick={{ fill: '#55534a', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#55534a', fontSize: 12 }} domain={['dataMin - 3', 'dataMax + 3']} />
                    <Tooltip
                      contentStyle={{ background: '#f5f5ef', border: '1px solid #1b1b16' }}
                      labelStyle={{ color: '#1b1b16' }}
                    />
                    <Line type="monotone" dataKey="score" stroke="#c23b2a" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>

          <div className="mt-6">
            <Link to="/rounds" className="text-sm text-ink underline underline-offset-2">
              전체 라운드 보기
            </Link>
          </div>
        </>
      )}
    </Layout>
  );
}
