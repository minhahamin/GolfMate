import { Link } from 'react-router-dom';

import golferRabbit from '../assets/golfer-rabbit.png';
import Layout from '../components/Layout';
import { useRounds } from '../hooks/useRounds';

export default function Rounds() {
  const { data: rounds, isLoading } = useRounds();

  return (
    <Layout>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-emerald-50">내 라운드</h1>
        <Link
          to="/rounds/new"
          className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-emerald-950 transition hover:bg-emerald-400"
        >
          라운드 등록
        </Link>
      </div>

      {isLoading ? (
        <p className="mt-8 text-sm text-emerald-200/60">불러오는 중...</p>
      ) : !rounds || rounds.length === 0 ? (
        <div className="mt-8 flex flex-col items-center gap-6 rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-8 text-center sm:flex-row sm:text-left">
          <img src={golferRabbit} alt="골프 캐디 토끼" className="h-32 w-32 rounded-xl object-cover" />
          <div>
            <p className="text-emerald-50">아직 등록된 라운드가 없어요.</p>
            <p className="mt-1 text-sm text-emerald-200/60">
              첫 라운드를 등록하고 통계를 쌓아보세요.
            </p>
          </div>
        </div>
      ) : (
        <div className="mt-6 divide-y divide-emerald-800/30 overflow-hidden rounded-2xl border border-emerald-800/40 bg-emerald-950/40">
          {rounds.map((round) => (
            <Link
              key={round.id}
              to={`/rounds/${round.id}`}
              className="flex items-center justify-between px-6 py-4 transition hover:bg-emerald-900/30"
            >
              <div>
                <p className="text-emerald-50">{round.course.name}</p>
                <p className="text-sm text-emerald-200/60">{round.round_date}</p>
              </div>
              <p className="text-xl font-semibold text-emerald-50">{round.score}</p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
