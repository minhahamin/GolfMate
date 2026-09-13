import { useEffect, useState, type FormEvent } from 'react';

import Layout from '../components/Layout';
import { useCourse, useCourses } from '../hooks/useCourses';
import { useCreateRound } from '../hooks/useRounds';
import type { HoleInput } from '../types/round';

function emptyHole(hole_number: number, par: number): HoleInput {
  return {
    hole_number,
    par,
    score: par,
    putts: 2,
    fairway_hit: false,
    gir: false,
    ob: 0,
    bunker: 0,
    penalty: 0,
  };
}

export default function RoundNew() {
  const { data: courses } = useCourses();
  const [courseId, setCourseId] = useState<number | null>(null);
  const { data: courseDetail } = useCourse(courseId ?? NaN);

  const [roundDate, setRoundDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [score, setScore] = useState('');
  const [weather, setWeather] = useState('');
  const [memo, setMemo] = useState('');
  const [useHoleDetail, setUseHoleDetail] = useState(false);
  const [holes, setHoles] = useState<HoleInput[]>([]);

  const createRound = useCreateRound();

  useEffect(() => {
    if (courses && courses.length > 0 && courseId === null) {
      setCourseId(courses[0].id);
    }
  }, [courses, courseId]);

  useEffect(() => {
    if (courseDetail) {
      setHoles(courseDetail.holes.map((h) => emptyHole(h.hole_number, h.par)));
    }
  }, [courseDetail]);

  function updateHole(index: number, patch: Partial<HoleInput>) {
    setHoles((prev) => prev.map((h, i) => (i === index ? { ...h, ...patch } : h)));
  }

  const holeScoreTotal = holes.reduce((sum, h) => sum + h.score, 0);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!courseId) return;

    createRound.mutate({
      course_id: courseId,
      round_date: roundDate,
      weather: weather || null,
      memo: memo || null,
      ...(useHoleDetail ? { holes } : { score: Number(score) }),
    });
  }

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-emerald-50">라운드 등록</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <section className="grid grid-cols-1 gap-4 rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6 sm:grid-cols-2">
          <label className="text-sm text-emerald-200/80">
            골프장
            <select
              value={courseId ?? ''}
              onChange={(e) => setCourseId(Number(e.target.value))}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            >
              {courses?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.region})
                </option>
              ))}
            </select>
          </label>

          <label className="text-sm text-emerald-200/80">
            라운드 날짜
            <input
              type="date"
              required
              value={roundDate}
              onChange={(e) => setRoundDate(e.target.value)}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            />
          </label>

          <label className="text-sm text-emerald-200/80">
            날씨
            <input
              type="text"
              placeholder="맑음, 흐림 등"
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            />
          </label>

          {!useHoleDetail && (
            <label className="text-sm text-emerald-200/80">
              총타수
              <input
                type="number"
                required={!useHoleDetail}
                value={score}
                onChange={(e) => setScore(e.target.value)}
                className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
              />
            </label>
          )}

          <label className="text-sm text-emerald-200/80 sm:col-span-2">
            메모
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              rows={2}
              className="mt-1 w-full rounded-lg border border-emerald-800/50 bg-black/20 px-3 py-2 text-emerald-50 outline-none focus:border-emerald-500"
            />
          </label>
        </section>

        <label className="flex items-center gap-2 text-sm text-emerald-200/80">
          <input
            type="checkbox"
            checked={useHoleDetail}
            onChange={(e) => setUseHoleDetail(e.target.checked)}
          />
          홀별 상세 기록 입력하기 (퍼팅/페어웨이/GIR 등 — 입력하면 총타수는 자동 계산됩니다)
        </label>

        {useHoleDetail && (
          <section className="overflow-x-auto rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-4">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="text-left text-emerald-300/70">
                  <th className="p-2">홀</th>
                  <th className="p-2">파</th>
                  <th className="p-2">스코어</th>
                  <th className="p-2">퍼팅</th>
                  <th className="p-2">페어웨이</th>
                  <th className="p-2">GIR</th>
                  <th className="p-2">OB</th>
                  <th className="p-2">벙커</th>
                  <th className="p-2">벌타</th>
                </tr>
              </thead>
              <tbody>
                {holes.map((hole, index) => (
                  <tr key={hole.hole_number} className="border-t border-emerald-900/50">
                    <td className="p-2 text-emerald-100">{hole.hole_number}</td>
                    <td className="p-2 text-emerald-200/70">{hole.par}</td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={hole.score}
                        onChange={(e) => updateHole(index, { score: Number(e.target.value) })}
                        className="w-16 rounded border border-emerald-800/50 bg-black/20 px-2 py-1 text-emerald-50"
                      />
                    </td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={hole.putts}
                        onChange={(e) => updateHole(index, { putts: Number(e.target.value) })}
                        className="w-14 rounded border border-emerald-800/50 bg-black/20 px-2 py-1 text-emerald-50"
                      />
                    </td>
                    <td className="p-2 text-center">
                      <input
                        type="checkbox"
                        disabled={hole.par === 3}
                        checked={hole.fairway_hit}
                        onChange={(e) => updateHole(index, { fairway_hit: e.target.checked })}
                      />
                    </td>
                    <td className="p-2 text-center">
                      <input
                        type="checkbox"
                        checked={hole.gir}
                        onChange={(e) => updateHole(index, { gir: e.target.checked })}
                      />
                    </td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={hole.ob}
                        onChange={(e) => updateHole(index, { ob: Number(e.target.value) })}
                        className="w-12 rounded border border-emerald-800/50 bg-black/20 px-2 py-1 text-emerald-50"
                      />
                    </td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={hole.bunker}
                        onChange={(e) => updateHole(index, { bunker: Number(e.target.value) })}
                        className="w-12 rounded border border-emerald-800/50 bg-black/20 px-2 py-1 text-emerald-50"
                      />
                    </td>
                    <td className="p-2">
                      <input
                        type="number"
                        value={hole.penalty}
                        onChange={(e) => updateHole(index, { penalty: Number(e.target.value) })}
                        className="w-12 rounded border border-emerald-800/50 bg-black/20 px-2 py-1 text-emerald-50"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-3 text-sm text-emerald-200/70">
              합계 스코어: <span className="font-semibold text-emerald-50">{holeScoreTotal}</span>
            </p>
          </section>
        )}

        {createRound.isError && (
          <p className="text-sm text-red-400">라운드 등록에 실패했습니다. 입력값을 확인해주세요.</p>
        )}

        <button
          type="submit"
          disabled={createRound.isPending || !courseId}
          className="rounded-lg bg-emerald-500 px-6 py-2 font-medium text-emerald-950 transition hover:bg-emerald-400 disabled:opacity-50"
        >
          {createRound.isPending ? '등록 중...' : '라운드 등록'}
        </button>
      </form>
    </Layout>
  );
}
