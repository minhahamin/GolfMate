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
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex items-start justify-between border-b border-ink/15 pb-6">
        <div>
          <h1 className="font-display text-3xl text-ink">{round.course.name}</h1>
          <p className="mt-2 flex gap-3 text-sm text-ink-soft">
            <span>{round.round_date}</span>
            <span className="border-l border-ink/20 pl-3">{round.weather ?? '날씨 미기록'}</span>
          </p>
        </div>
        <div className="text-right">
          <p className="font-mono text-4xl text-ink">{round.score}</p>
          {analysis?.score_to_par != null && (
            <p className="text-sm text-ink-soft">
              {analysis.score_to_par > 0 ? `+${analysis.score_to_par}` : analysis.score_to_par}
            </p>
          )}
        </div>
      </div>

      {round.memo && (
        <p className="mt-4 border border-ink/15 bg-paper-2 p-4 text-sm text-ink-soft">
          {round.memo}
        </p>
      )}

      {analysis?.has_hole_detail && (
        <section className="mt-6 border border-ink/15 p-6">
          <h2 className="font-display text-lg text-ink">🤖 AI 분석</h2>
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
          <div className="mt-4 grid grid-cols-3 divide-x divide-ink/15 border-t border-ink/15 pt-4 text-center text-sm">
            <div>
              <p className="text-ink-soft">파3 평균</p>
              <p className="mt-1 font-mono text-lg text-ink">{analysis.par3_average ?? '—'}</p>
            </div>
            <div>
              <p className="text-ink-soft">파4 평균</p>
              <p className="mt-1 font-mono text-lg text-ink">{analysis.par4_average ?? '—'}</p>
            </div>
            <div>
              <p className="text-ink-soft">파5 평균</p>
              <p className="mt-1 font-mono text-lg text-ink">{analysis.par5_average ?? '—'}</p>
            </div>
          </div>
          <p className="mt-4 text-xs text-ink-soft">
            OB {analysis.ob_count}회 / 벙커 {analysis.bunker_count}회 / 벌타 {analysis.penalty_count}회
          </p>
        </section>
      )}

      {round.holes.length > 0 && (
        <section className="mt-6 overflow-x-auto border border-ink/15 p-4">
          <table className="w-full min-w-[520px] text-sm">
            <thead>
              <tr className="text-left text-ink-soft">
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
                <tr key={hole.hole_number} className="border-t border-ink/10">
                  <td className="p-2 font-mono text-ink">{hole.hole_number}</td>
                  <td className="p-2 font-mono text-ink-soft">{hole.par}</td>
                  <td className="p-2 font-mono text-ink">{hole.score}</td>
                  <td className="p-2 font-mono text-ink">{hole.putts}</td>
                  <td className="p-2">{hole.par === 3 ? '—' : hole.fairway_hit ? 'O' : 'X'}</td>
                  <td className="p-2">{hole.gir ? 'O' : 'X'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <div className="mt-6 flex gap-4">
        <button
          onClick={() => navigate('/rounds')}
          className="text-sm text-ink underline underline-offset-2"
        >
          목록으로
        </button>
        <button
          onClick={() => {
            if (window.confirm('이 라운드를 삭제할까요?')) {
              deleteRound.mutate(roundId);
            }
          }}
          className="text-sm text-flag underline underline-offset-2"
        >
          라운드 삭제
        </button>
      </div>
    </Layout>
  );
}
