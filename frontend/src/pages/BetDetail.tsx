import { useNavigate, useParams } from 'react-router-dom';

import { getBetCommentaryErrorMessage } from '../api/bets';
import Layout from '../components/Layout';
import { useBetCommentary } from '../hooks/useBetCommentary';
import { useBet } from '../hooks/useBets';

export default function BetDetail() {
  const { id } = useParams();
  const betId = Number(id);
  const navigate = useNavigate();

  const { data: bet, isLoading } = useBet(betId);
  const commentary = useBetCommentary();

  if (isLoading || !bet) {
    return (
      <Layout>
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  const sortedResults = [...bet.results].sort((a, b) => b.payout_amount - a.payout_amount);

  return (
    <Layout>
      <div className="border-b border-ink/15 pb-6">
        <h1 className="font-display text-3xl text-ink">{bet.title}</h1>
        <p className="mt-1 text-sm text-ink-soft">
          {bet.bet_date} · {bet.course_name} · 타당 {bet.stake_per_stroke.toLocaleString()}원
        </p>
      </div>

      <section className="mt-6 overflow-x-auto border border-ink/15 p-4">
        <table className="w-full min-w-[420px] text-sm">
          <thead>
            <tr className="text-left text-ink-soft">
              <th className="p-2">참가자</th>
              <th className="p-2">스코어</th>
              <th className="p-2">정산 금액</th>
            </tr>
          </thead>
          <tbody>
            {sortedResults.map((r) => (
              <tr key={r.user_id} className="border-t border-ink/10">
                <td className="p-2 text-ink">{r.name}</td>
                <td className="p-2 font-mono text-ink">{r.score}</td>
                <td
                  className={`p-2 font-mono ${
                    r.payout_amount > 0 ? 'text-fairway-deep' : r.payout_amount < 0 ? 'text-flag' : 'text-ink-soft'
                  }`}
                >
                  {r.payout_amount > 0 ? '+' : ''}
                  {r.payout_amount.toLocaleString()}원
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="mt-6 border border-ink/15 p-6">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg text-ink">🤖 AI 코멘터리</h2>
          <button
            onClick={() => commentary.mutate(betId)}
            disabled={commentary.isPending}
            className="bg-flag px-4 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
          >
            {commentary.isPending ? '생성 중...' : '코멘터리 받기'}
          </button>
        </div>
        {commentary.isError && (
          <p className="mt-3 text-sm text-flag">{getBetCommentaryErrorMessage(commentary.error)}</p>
        )}
        {commentary.data && (
          <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-ink-soft">
            {commentary.data.commentary}
          </p>
        )}
      </section>

      <button
        onClick={() => navigate(`/groups/${bet.group_id}`)}
        className="mt-6 text-sm text-ink underline underline-offset-2"
      >
        모임으로
      </button>
    </Layout>
  );
}
