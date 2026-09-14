import { useEffect, useState, type FormEvent } from 'react';

import { getCaddieRequestErrorMessage } from '../api/caddie';
import Layout from '../components/Layout';
import { useCaddie } from '../hooks/useCaddie';
import { useCourse, useCourses } from '../hooks/useCourses';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

const SECTIONS: { key: 'hole_analysis' | 'risk_analysis' | 'club_strategy'; label: string }[] = [
  { key: 'hole_analysis', label: '홀공략' },
  { key: 'risk_analysis', label: '위험요소' },
  { key: 'club_strategy', label: '클럽전략' },
];

export default function Caddie() {
  const { data: courses } = useCourses();
  const [courseId, setCourseId] = useState<number | null>(null);
  const { data: courseDetail } = useCourse(courseId ?? NaN);

  const [holeNumber, setHoleNumber] = useState<number | null>(null);
  const [question, setQuestion] = useState('');

  const caddie = useCaddie();

  useEffect(() => {
    if (courses && courses.length > 0 && courseId === null) {
      setCourseId(courses[0].id);
    }
  }, [courses, courseId]);

  useEffect(() => {
    if (courseDetail && courseDetail.holes.length > 0) {
      setHoleNumber(courseDetail.holes[0].hole_number);
    }
  }, [courseDetail]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!courseId || !holeNumber) return;
    caddie.mutate({ course_id: courseId, hole_number: holeNumber, question: question || undefined });
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">🤖 AI 캐디</h1>
      <p className="mt-1 text-sm text-ink-soft">
        골프장과 홀을 고르면, 지금 실제 날씨를 반영해 공략법을 알려드려요.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-1 gap-4 border border-ink/15 p-6 sm:grid-cols-2">
        <label className="text-sm text-ink-soft">
          골프장
          <select
            value={courseId ?? ''}
            onChange={(e) => setCourseId(Number(e.target.value))}
            className={fieldClass}
          >
            {courses?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.region})
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-ink-soft">
          홀
          <select
            value={holeNumber ?? ''}
            onChange={(e) => setHoleNumber(Number(e.target.value))}
            className={fieldClass}
          >
            {courseDetail?.holes.map((h) => (
              <option key={h.hole_number} value={h.hole_number}>
                {h.hole_number}번 (파{h.par}, {h.distance_meters}m)
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-ink-soft sm:col-span-2">
          궁금한 점 (선택)
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="예: 왼쪽에 OB가 있는데 어떻게 쳐야 할까?"
            rows={2}
            className={fieldClass}
          />
        </label>

        <button
          type="submit"
          disabled={caddie.isPending || !courseId || !holeNumber}
          className="bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50 sm:col-span-2 sm:w-fit"
        >
          {caddie.isPending ? '분석 중... (최대 45초 정도 걸려요)' : '공략 받기'}
        </button>
      </form>

      {caddie.isError && (
        <p className="mt-6 text-sm text-flag">{getCaddieRequestErrorMessage(caddie.error)}</p>
      )}

      {caddie.data && (
        <div className="mt-6">
          {caddie.data.weather_summary && (
            <p className="border border-ink/15 bg-paper-2 px-4 py-3 text-sm text-ink-soft">
              🌤 현재 날씨: {caddie.data.weather_summary}
            </p>
          )}

          <div className="mt-6 divide-y divide-ink/15 border-y border-ink/15">
            {SECTIONS.map(({ key, label }) =>
              caddie.data![key] ? (
                <div key={key} className="py-5">
                  <p className="font-display text-lg text-ink">{label}</p>
                  <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-soft">
                    {caddie.data![key]}
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
