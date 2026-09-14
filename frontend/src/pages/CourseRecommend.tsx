import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';

import { getRecommendRequestErrorMessage } from '../api/recommend';
import Layout from '../components/Layout';
import { useCourseRecommendation } from '../hooks/useRecommend';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

const DIFFICULTY_OPTIONS = ['전체', '초급', '중급', '고급'];

export default function CourseRecommend() {
  const [region, setRegion] = useState('');
  const [difficulty, setDifficulty] = useState('전체');
  const [maxBudget, setMaxBudget] = useState('');
  const [preferenceText, setPreferenceText] = useState('');

  const recommend = useCourseRecommendation();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    recommend.mutate({
      region: region.trim() || undefined,
      difficulty: difficulty === '전체' ? undefined : difficulty,
      max_budget: maxBudget ? Number(maxBudget) : undefined,
      preference_text: preferenceText.trim() || undefined,
    });
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">🤖 AI 골프장 추천</h1>
      <p className="mt-1 text-sm text-ink-soft">
        조건을 입력하면 실제 등록된 골프장 중에서 AI가 어울리는 곳을 골라드려요.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-1 gap-4 border border-ink/15 p-6 sm:grid-cols-2">
        <label className="text-sm text-ink-soft">
          지역 (선택)
          <input
            type="text"
            placeholder="예: 경기도, 제주도"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className="text-sm text-ink-soft">
          난이도
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className={fieldClass}>
            {DIFFICULTY_OPTIONS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-ink-soft">
          예산 (그린피, 원 이하 — 선택)
          <input
            type="number"
            placeholder="예: 150000"
            value={maxBudget}
            onChange={(e) => setMaxBudget(e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className="text-sm text-ink-soft sm:col-span-2">
          원하는 분위기/조건 (선택)
          <textarea
            value={preferenceText}
            onChange={(e) => setPreferenceText(e.target.value)}
            placeholder="예: 바다가 보이는 곳으로 추천해줘"
            rows={2}
            className={fieldClass}
          />
        </label>

        <button
          type="submit"
          disabled={recommend.isPending}
          className="bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50 sm:col-span-2 sm:w-fit"
        >
          {recommend.isPending ? '추천 받는 중...' : '추천 받기'}
        </button>
      </form>

      {recommend.isError && (
        <p className="mt-6 text-sm text-flag">{getRecommendRequestErrorMessage(recommend.error)}</p>
      )}

      {recommend.data && (
        <div className="mt-6">
          <p className="text-sm leading-relaxed text-ink-soft">{recommend.data.summary}</p>

          {recommend.data.recommendations.length > 0 && (
            <div className="mt-6 divide-y divide-ink/15 border-y border-ink/15">
              {recommend.data.recommendations.map(({ course, reason }, index) => (
                <div key={course.id} className="py-5">
                  <div className="flex items-center justify-between">
                    <Link to={`/courses/${course.id}`} className="font-display text-lg text-ink hover:underline">
                      {index + 1}위 · {course.name}
                    </Link>
                    <p className="font-mono text-sm text-ink-soft">
                      {course.green_fee_avg != null ? `${course.green_fee_avg.toLocaleString()}원` : '가격 미상'}
                    </p>
                  </div>
                  <p className="text-sm text-ink-soft">
                    {course.region} · 난이도 {course.difficulty}
                  </p>
                  <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-soft">{reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}
