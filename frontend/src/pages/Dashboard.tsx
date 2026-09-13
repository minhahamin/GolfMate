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

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-emerald-800/40 bg-emerald-950/40 p-4">
      <p className="text-xs uppercase tracking-wide text-emerald-300/70">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-emerald-50">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const { data: profile } = useMyProfile();
  const { data: stats, isLoading } = useStatisticsSummary(10);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-emerald-50">{user?.name}님, 안녕하세요</h1>
      <p className="mt-1 text-sm text-emerald-200/60">최근 10라운드 기준 통계입니다.</p>

      {isLoading ? (
        <p className="mt-8 text-sm text-emerald-200/60">불러오는 중...</p>
      ) : !stats || stats.rounds_count === 0 ? (
        <div className="mt-8 flex flex-col items-center gap-6 rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-8 text-center sm:flex-row sm:text-left">
          <img src={golferRabbit} alt="골프 캐디 토끼" className="h-40 w-40 rounded-xl object-cover" />
          <div>
            <h2 className="text-lg font-medium text-emerald-50">아직 기록된 라운드가 없어요</h2>
            <p className="mt-1 text-sm text-emerald-200/60">
              첫 라운드를 등록하면 평균 스코어, 퍼팅, 페어웨이 적중률 같은 통계가 여기 쌓입니다.
            </p>
            <Link
              to="/rounds/new"
              className="mt-4 inline-block rounded-lg bg-emerald-500 px-5 py-2 text-sm font-medium text-emerald-950 transition hover:bg-emerald-400"
            >
              라운드 등록하기
            </Link>
          </div>
        </div>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatCard label="핸디캡" value={profile?.handicap?.toString() ?? '-'} />
            <StatCard label="평균 스코어" value={stats.average_score?.toString() ?? '-'} />
            <StatCard label="베스트 스코어" value={stats.best_score?.toString() ?? '-'} />
            <StatCard label="기록된 라운드" value={`${stats.rounds_count}회`} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6">
              <h2 className="text-sm font-medium text-emerald-50">🤖 AI 분석 (계산 기반)</h2>
              <p className="mt-1 text-xs text-emerald-200/50">
                최근 10라운드 기준 — AI 코치는 Phase 4에서 이 데이터를 바탕으로 조언합니다.
              </p>
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

            <section className="rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6">
              <h2 className="text-sm font-medium text-emerald-50">스코어 추이</h2>
              <div className="mt-4 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats.recent_rounds}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#065f46" />
                    <XAxis dataKey="round_date" tick={{ fill: '#a7f3d0', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#a7f3d0', fontSize: 12 }} domain={['dataMin - 3', 'dataMax + 3']} />
                    <Tooltip
                      contentStyle={{ background: '#022c22', border: '1px solid #065f46' }}
                      labelStyle={{ color: '#d1fae5' }}
                    />
                    <Line type="monotone" dataKey="score" stroke="#34d399" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>

          <div className="mt-6 flex justify-end">
            <Link to="/rounds" className="text-sm text-emerald-400 hover:underline">
              전체 라운드 보기 →
            </Link>
          </div>
        </>
      )}
    </Layout>
  );
}
