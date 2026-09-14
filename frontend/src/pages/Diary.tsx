import { Link } from 'react-router-dom';

import golferRabbit from '../assets/golfer-rabbit.png';
import Layout from '../components/Layout';
import { useDiaries } from '../hooks/useDiary';

export default function Diary() {
  const { data: diaries, isLoading } = useDiaries();

  return (
    <Layout>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-ink">AI 일기</h1>
        <Link
          to="/diary/new"
          className="bg-flag px-4 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
        >
          새 일기 쓰기
        </Link>
      </div>
      <p className="mt-1 text-sm text-ink-soft">
        라운드 소감을 텍스트나 음성으로 남기면, AI가 기분·하이라이트·개선점을 정리해줘요.
      </p>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : !diaries || diaries.length === 0 ? (
        <div className="mt-8 flex flex-col items-center gap-6 border border-ink/15 bg-paper-2 p-8 sm:flex-row">
          <div className="w-24 shrink-0 overflow-hidden rounded border border-ink/15 shadow-[3px_3px_0_0_var(--ink)]">
            <img src={golferRabbit} alt="골프 캐디 토끼" className="aspect-square w-full object-cover" />
          </div>
          <div>
            <p className="text-ink">아직 작성된 일기가 없어요.</p>
            <p className="mt-1 text-sm text-ink-soft">첫 라운드 소감을 남겨보세요.</p>
          </div>
        </div>
      ) : (
        <div className="mt-6 divide-y divide-ink/15 border-y border-ink/15">
          {diaries.map((diary) => (
            <Link
              key={diary.id}
              to={`/diary/${diary.id}`}
              className="flex items-center justify-between gap-4 px-2 py-4 transition hover:bg-paper-2"
            >
              <div className="min-w-0">
                <p className="text-sm text-ink-soft">{diary.created_at.slice(0, 10)}</p>
                <p className="mt-1 truncate text-ink">{diary.summary}</p>
              </div>
              <p className="shrink-0 font-display text-sm text-ink-soft">{diary.mood}</p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
