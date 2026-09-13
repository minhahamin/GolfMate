import { Link } from 'react-router-dom';

import golferRabbit from '../assets/golfer-rabbit.png';
import Layout from '../components/Layout';
import { useRounds } from '../hooks/useRounds';

export default function Rounds() {
  const { data: rounds, isLoading } = useRounds();

  return (
    <Layout>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-ink">내 라운드</h1>
        <Link
          to="/rounds/new"
          className="bg-flag px-4 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
        >
          라운드 등록
        </Link>
      </div>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : !rounds || rounds.length === 0 ? (
        <div className="mt-8 flex flex-col items-center gap-6 border border-ink/15 bg-paper-2 p-8 sm:flex-row">
          <div className="w-24 shrink-0 overflow-hidden rounded border border-ink/15 shadow-[3px_3px_0_0_var(--ink)]">
            <img src={golferRabbit} alt="골프 캐디 토끼" className="aspect-square w-full object-cover" />
          </div>
          <div>
            <p className="text-ink">아직 등록된 라운드가 없어요.</p>
            <p className="mt-1 text-sm text-ink-soft">첫 라운드를 등록하고 통계를 쌓아보세요.</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 divide-y divide-ink/15 border-y border-ink/15">
          {rounds.map((round) => (
            <Link
              key={round.id}
              to={`/rounds/${round.id}`}
              className="flex items-center justify-between px-2 py-4 transition hover:bg-paper-2"
            >
              <div>
                <p className="text-ink">{round.course.name}</p>
                <p className="text-sm text-ink-soft">{round.round_date}</p>
              </div>
              <p className="font-mono text-xl text-ink">{round.score}</p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
