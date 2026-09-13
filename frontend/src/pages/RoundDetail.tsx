import { useNavigate, useParams } from 'react-router-dom';

import Layout from '../components/Layout';
import StatBar from '../components/StatBar';
import { useRoundAnalysis } from '../hooks/useRoundAnalysis';
import { useDeleteRound, useRound } from '../hooks/useRounds';

export default function RoundDetail() {
  const { id } = useParams();
  const roundId = Number(id);
  const navigate = useNavigate();

  const { data: round, isLoading } = useRound(roundId);
  const { data: analysis } = useRoundAnalysis(roundId);
  const deleteRound = useDeleteRound();

  if (isLoading || !round) {
    return (
      <Layout>
        <p className="text-sm text-emerald-200/60">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-emerald-50">{round.course.name}</h1>
          <p className="mt-1 text-sm text-emerald-200/60">
            {round.round_date} · {round.weather ?? '날씨 미기록'}
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-semibold text-emerald-50">{round.score}</p>
          {analysis?.score_to_par != null && (
            <p className="text-sm text-emerald-200/60">
              {analysis.score_to_par > 0 ? `+${analysis.score_to_par}` : analysis.score_to_par}
            </p>
          )}
        </div>
      </div>

      {round.memo && (
        <p className="mt-4 rounded-lg border border-emerald-800/40 bg-emerald-950/40 p-4 text-sm text-emerald-200/80">
          {round.memo}
        </p>
      )}

      {analysis?.has_hole_detail && (
        <section className="mt-6 rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-6">
          <h2 className="text-sm font-medium text-emerald-50">🤖 AI 분석 (계산 기반)</h2>
          <div className="mt-4 space-y-4">
            {analysis.fairway_hit_rate != null && (
              <StatBar label="페어웨이 적중률" value={analysis.fairway_hit_rate} />
            )}
            {analysis.gir_rate != null && <StatBar label="GIR" value={analysis.gir_rate} />}
            {analysis.putts_average != null && (
              <StatBar
                label="홀당 평균 퍼팅"
                value={Math.min((analysis.putts_average / 2) * 100, 100)}
                displayValue={`${analysis.putts_average}개`}
              />
            )}
          </div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center text-sm">
            <div>
              <p className="text-emerald-200/60">파3 평균</p>
              <p className="text-lg text-emerald-50">{analysis.par3_average ?? '-'}</p>
            </div>
            <div>
              <p className="text-emerald-200/60">파4 평균</p>
              <p className="text-lg text-emerald-50">{analysis.par4_average ?? '-'}</p>
            </div>
            <div>
              <p className="text-emerald-200/60">파5 평균</p>
              <p className="text-lg text-emerald-50">{analysis.par5_average ?? '-'}</p>
            </div>
          </div>
          <p className="mt-4 text-xs text-emerald-200/50">
            OB {analysis.ob_count}회 · 벙커 {analysis.bunker_count}회 · 벌타 {analysis.penalty_count}회
          </p>
        </section>
      )}

      {round.holes.length > 0 && (
        <section className="mt-6 overflow-x-auto rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-4">
          <table className="w-full min-w-[520px] text-sm">
            <thead>
              <tr className="text-left text-emerald-300/70">
                <th className="p-2">홀</th>
                <th className="p-2">파</th>
                <th className="p-2">스코어</th>
                <th className="p-2">퍼팅</th>
                <th className="p-2">페어웨이</th>
                <th className="p-2">GIR</th>
              </tr>
            </thead>
            <tbody>
              {round.holes.map((hole) => (
                <tr key={hole.hole_number} className="border-t border-emerald-900/50">
                  <td className="p-2 text-emerald-100">{hole.hole_number}</td>
                  <td className="p-2 text-emerald-200/70">{hole.par}</td>
                  <td className="p-2 text-emerald-50">{hole.score}</td>
                  <td className="p-2 text-emerald-50">{hole.putts}</td>
                  <td className="p-2">{hole.par === 3 ? '-' : hole.fairway_hit ? 'O' : 'X'}</td>
                  <td className="p-2">{hole.gir ? 'O' : 'X'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <button
        onClick={() => {
          if (window.confirm('이 라운드를 삭제할까요?')) {
            deleteRound.mutate(roundId);
          }
        }}
        className="mt-6 text-sm text-red-400 hover:underline"
      >
        라운드 삭제
      </button>
      <button
        onClick={() => navigate('/rounds')}
        className="ml-4 mt-6 text-sm text-emerald-300/70 hover:underline"
      >
        목록으로
      </button>
    </Layout>
  );
}
