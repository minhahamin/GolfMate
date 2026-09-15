import { useNavigate, useParams } from 'react-router-dom';

import Layout from '../components/Layout';
import SpeakButton from '../components/SpeakButton';
import { useDeleteDiary, useDiary } from '../hooks/useDiary';

const SECTIONS: { key: 'mood' | 'highlights' | 'improvement_points' | 'next_goal'; label: string }[] = [
  { key: 'mood', label: '기분' },
  { key: 'highlights', label: '하이라이트' },
  { key: 'improvement_points', label: '개선점' },
  { key: 'next_goal', label: '다음 목표' },
];

export default function DiaryDetail() {
  const { id } = useParams();
  const diaryId = Number(id);
  const navigate = useNavigate();

  const { data: diary, isLoading } = useDiary(diaryId);
  const deleteDiary = useDeleteDiary();

  if (isLoading || !diary) {
    return (
      <Layout>
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="border-b border-ink/15 pb-6">
        <p className="text-sm text-ink-soft">{diary.created_at.slice(0, 10)}</p>
        <h1 className="mt-1 font-display text-3xl text-ink">{diary.summary}</h1>
        {diary.round_summary && (
          <p className="mt-2 text-sm text-ink-soft">연결된 라운드: {diary.round_summary}</p>
        )}
      </div>

      <section className="mt-6 border border-ink/15 p-6">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg text-ink">🤖 AI 정리</h2>
          <SpeakButton
            text={[
              `요약. ${diary.summary}`,
              ...SECTIONS.map(({ key, label }) => (diary[key] ? `${label}. ${diary[key]}` : null)),
            ]
              .filter(Boolean)
              .join('\n\n')}
          />
        </div>
        <div className="mt-4 divide-y divide-ink/15">
          {SECTIONS.map(({ key, label }) =>
            diary[key] ? (
              <div key={key} className="py-4 first:pt-0">
                <p className="font-display text-base text-ink">{label}</p>
                <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-soft">
                  {diary[key]}
                </p>
              </div>
            ) : null,
          )}
        </div>
      </section>

      <section className="mt-6 border border-ink/15 bg-paper-2 p-6">
        <h2 className="font-display text-lg text-ink">원문</h2>
        <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-ink-soft">
          {diary.raw_text}
        </p>
      </section>

      <div className="mt-6 flex gap-4">
        <button
          onClick={() => navigate('/diary')}
          className="text-sm text-ink underline underline-offset-2"
        >
          목록으로
        </button>
        <button
          onClick={() => {
            if (window.confirm('이 일기를 삭제할까요?')) {
              deleteDiary.mutate(diaryId);
            }
          }}
          className="text-sm text-flag underline underline-offset-2"
        >
          일기 삭제
        </button>
      </div>
    </Layout>
  );
}
