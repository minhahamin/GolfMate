import { useState, type FormEvent } from 'react';

import { getCoachRequestErrorMessage } from '../api/coach';
import Layout from '../components/Layout';
import SpeakButton from '../components/SpeakButton';
import { useCoach } from '../hooks/useCoach';

const SECTIONS: { key: 'current_state' | 'biggest_problem' | 'cause' | 'strategy' | 'next_goal'; label: string }[] = [
  { key: 'current_state', label: '현재 상태' },
  { key: 'biggest_problem', label: '가장 큰 문제' },
  { key: 'cause', label: '문제의 원인' },
  { key: 'strategy', label: '추천 전략' },
  { key: 'next_goal', label: '다음 라운드 목표' },
];

export default function Coach() {
  const [question, setQuestion] = useState('');
  const coach = useCoach();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    coach.mutate(question);
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">🤖 AI 코치</h1>
      <p className="mt-1 text-sm text-ink-soft">
        최근 라운드 데이터를 바탕으로 가장 큰 약점과 개선 전략을 분석해드려요.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 border border-ink/15 p-6">
        <label className="block text-sm text-ink-soft">
          궁금한 점이 있나요? (선택)
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="예: 최근 스코어가 안 줄어드는데 뭐가 문제일까요?"
            rows={2}
            className="mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink"
          />
        </label>
        <button
          type="submit"
          disabled={coach.isPending}
          className="mt-4 bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
        >
          {coach.isPending ? '분석 중... (최대 30초 정도 걸려요)' : '분석 받기'}
        </button>
      </form>

      {coach.isError && (
        <p className="mt-6 text-sm text-flag">{getCoachRequestErrorMessage(coach.error)}</p>
      )}

      {coach.data && (
        <div className="mt-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-ink-soft">분석 결과</p>
            <SpeakButton
              text={SECTIONS.map(({ key, label }) => (coach.data![key] ? `${label}. ${coach.data![key]}` : null))
                .filter(Boolean)
                .join('\n\n')}
            />
          </div>
          <div className="mt-2 divide-y divide-ink/15 border-y border-ink/15">
            {SECTIONS.map(({ key, label }) =>
              coach.data![key] ? (
                <div key={key} className="py-5">
                  <p className="font-display text-lg text-ink">{label}</p>
                  <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-soft">
                    {coach.data![key]}
                  </p>
                </div>
              ) : null,
            )}
          </div>
        </div>
      )}
    </Layout>
  );
}
