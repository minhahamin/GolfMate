import { useEffect, useState, type FormEvent } from 'react';
import { useParams } from 'react-router-dom';

import Layout from '../components/Layout';
import { useGroup } from '../hooks/useGroups';
import { useCreateBet } from '../hooks/useBets';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

export default function BetNew() {
  const { id } = useParams();
  const groupId = Number(id);
  const { data: group } = useGroup(groupId);
  const createBet = useCreateBet(groupId);

  const [title, setTitle] = useState('');
  const [betDate, setBetDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [courseName, setCourseName] = useState('');
  const [stakePerStroke, setStakePerStroke] = useState('1000');
  const [scores, setScores] = useState<Record<number, string>>({});

  useEffect(() => {
    if (group) {
      setScores((prev) => {
        const next = { ...prev };
        for (const member of group.members) {
          if (!(member.user_id in next)) next[member.user_id] = '';
        }
        return next;
      });
    }
  }, [group]);

  const participantCount = group?.members.filter((m) => scores[m.user_id] !== '').length ?? 0;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!group || participantCount < 2) return;

    const scorePayload: Record<number, number> = {};
    for (const member of group.members) {
      const value = scores[member.user_id];
      if (value !== '') scorePayload[member.user_id] = Number(value);
    }

    createBet.mutate({
      title: title.trim(),
      bet_date: betDate,
      course_name: courseName.trim(),
      stake_per_stroke: Number(stakePerStroke),
      scores: scorePayload,
    });
  }

  if (!group) {
    return (
      <Layout>
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">새 내기 기록</h1>
      <p className="mt-1 text-sm text-ink-soft">{group.name} — 타당 내기 (스코어가 낮을수록 이깁니다)</p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <section className="grid grid-cols-1 gap-4 border border-ink/15 p-6 sm:grid-cols-2">
          <label className="text-sm text-ink-soft">
            내기 이름
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예: 주말 라운드 내기"
              className={fieldClass}
            />
          </label>

          <label className="text-sm text-ink-soft">
            날짜
            <input
              type="date"
              required
              value={betDate}
              onChange={(e) => setBetDate(e.target.value)}
              className={fieldClass}
            />
          </label>

          <label className="text-sm text-ink-soft">
            골프장
            <input
              type="text"
              required
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              placeholder="예: 그린힐 컨트리클럽"
              className={fieldClass}
            />
          </label>

          <label className="text-sm text-ink-soft">
            타당 금액 (원)
            <input
              type="number"
              required
              min={0}
              value={stakePerStroke}
              onChange={(e) => setStakePerStroke(e.target.value)}
              className={fieldClass}
            />
          </label>
        </section>

        <section className="border border-ink/15 p-6">
          <p className="text-sm text-ink-soft">참가자 스코어 (2명 이상 입력)</p>
          <div className="mt-3 space-y-3">
            {group.members.map((member) => (
              <label key={member.user_id} className="flex items-center justify-between gap-4 text-sm text-ink-soft">
                <span className="text-ink">{member.name}</span>
                <input
                  type="number"
                  value={scores[member.user_id] ?? ''}
                  onChange={(e) =>
                    setScores((prev) => ({ ...prev, [member.user_id]: e.target.value }))
                  }
                  placeholder="타수"
                  className="w-28 border border-ink/20 bg-transparent px-3 py-1.5 font-mono text-ink outline-none focus:border-ink"
                />
              </label>
            ))}
          </div>
        </section>

        {createBet.isError && (
          <p className="text-sm text-flag">내기 등록에 실패했습니다. 입력값을 확인해주세요.</p>
        )}

        <button
          type="submit"
          disabled={createBet.isPending || participantCount < 2 || !title.trim() || !courseName.trim()}
          className="bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
        >
          {createBet.isPending ? '정산 중...' : '내기 등록 및 정산'}
        </button>
      </form>
    </Layout>
  );
}
