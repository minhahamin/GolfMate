import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { useAddGroupMember, useGroup, useRemoveGroupMember } from '../hooks/useGroups';
import { useBets } from '../hooks/useBets';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

export default function GroupDetail() {
  const { id } = useParams();
  const groupId = Number(id);
  const navigate = useNavigate();
  const { user } = useAuth();

  const { data: group, isLoading } = useGroup(groupId);
  const { data: bets } = useBets(groupId);
  const addMember = useAddGroupMember(groupId);
  const removeMember = useRemoveGroupMember(groupId);

  const [email, setEmail] = useState('');

  if (isLoading || !group) {
    return (
      <Layout>
        <p className="text-sm text-ink-soft">불러오는 중...</p>
      </Layout>
    );
  }

  const isOwner = group.owner_id === user?.id;

  function handleAddMember(event: FormEvent) {
    event.preventDefault();
    if (!email.trim()) return;
    addMember.mutate(email.trim(), { onSuccess: () => setEmail('') });
  }

  return (
    <Layout>
      <div className="flex items-start justify-between border-b border-ink/15 pb-6">
        <div>
          <h1 className="font-display text-3xl text-ink">{group.name}</h1>
          <p className="mt-1 text-sm text-ink-soft">멤버 {group.members.length}명</p>
        </div>
        <Link
          to={`/groups/${groupId}/bets/new`}
          className="bg-flag px-4 py-2 text-sm font-medium text-paper transition hover:bg-flag-deep"
        >
          새 내기 기록
        </Link>
      </div>

      <section className="mt-6 border border-ink/15 p-6">
        <h2 className="font-display text-lg text-ink">멤버</h2>
        <div className="mt-3 divide-y divide-ink/10">
          {group.members.map((member) => (
            <div key={member.user_id} className="flex items-center justify-between py-2 text-sm">
              <span className="text-ink">
                {member.name} {member.user_id === group.owner_id && <span className="text-ink-soft">(그룹장)</span>}
              </span>
              {(isOwner || member.user_id === user?.id) && member.user_id !== group.owner_id && (
                <button
                  onClick={() => removeMember.mutate(member.user_id)}
                  className="text-xs text-flag underline underline-offset-2"
                >
                  {member.user_id === user?.id ? '나가기' : '제거'}
                </button>
              )}
            </div>
          ))}
        </div>

        {isOwner && (
          <form onSubmit={handleAddMember} className="mt-4 flex items-end gap-3">
            <label className="flex-1 text-sm text-ink-soft">
              이메일로 멤버 추가
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="friend@example.com"
                className={fieldClass}
              />
            </label>
            <button
              type="submit"
              disabled={addMember.isPending}
              className="border border-ink/20 px-4 py-2 text-sm text-ink transition hover:bg-paper-2 disabled:opacity-50"
            >
              추가
            </button>
          </form>
        )}
        {addMember.isError && <p className="mt-2 text-sm text-flag">멤버 추가에 실패했습니다. 이메일을 확인해주세요.</p>}
      </section>

      <section className="mt-6">
        <h2 className="font-display text-lg text-ink">내기 기록</h2>
        {!bets || bets.length === 0 ? (
          <p className="mt-3 text-sm text-ink-soft">아직 기록된 내기가 없어요.</p>
        ) : (
          <div className="mt-3 divide-y divide-ink/15 border-y border-ink/15">
            {bets.map((bet) => (
              <Link
                key={bet.id}
                to={`/bets/${bet.id}`}
                className="flex items-center justify-between px-2 py-4 transition hover:bg-paper-2"
              >
                <div>
                  <p className="text-ink">{bet.title}</p>
                  <p className="text-sm text-ink-soft">
                    {bet.bet_date} · {bet.course_name}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      <button onClick={() => navigate('/groups')} className="mt-6 text-sm text-ink underline underline-offset-2">
        목록으로
      </button>
    </Layout>
  );
}
