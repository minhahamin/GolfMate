import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';

import Layout from '../components/Layout';
import { useCreateGroup, useGroups } from '../hooks/useGroups';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

export default function Groups() {
  const { data: groups, isLoading } = useGroups();
  const [name, setName] = useState('');
  const createGroup = useCreateGroup();

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    createGroup.mutate(name.trim());
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">내기 모임</h1>
      <p className="mt-1 text-sm text-ink-soft">
        친구들과 그룹을 만들고, 라운드 내기 결과를 기록하고 정산해보세요.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 flex items-end gap-3 border border-ink/15 p-6">
        <label className="flex-1 text-sm text-ink-soft">
          새 모임 이름
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="예: 주말 골프 모임"
            className={fieldClass}
          />
        </label>
        <button
          type="submit"
          disabled={createGroup.isPending || !name.trim()}
          className="bg-flag px-5 py-2.5 text-sm font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
        >
          {createGroup.isPending ? '생성 중...' : '모임 만들기'}
        </button>
      </form>

      {isLoading ? (
        <p className="mt-8 text-sm text-ink-soft">불러오는 중...</p>
      ) : !groups || groups.length === 0 ? (
        <p className="mt-8 text-sm text-ink-soft">아직 속한 모임이 없어요. 위에서 새 모임을 만들어보세요.</p>
      ) : (
        <div className="mt-6 divide-y divide-ink/15 border-y border-ink/15">
          {groups.map((group) => (
            <Link
              key={group.id}
              to={`/groups/${group.id}`}
              className="flex items-center justify-between px-2 py-4 transition hover:bg-paper-2"
            >
              <p className="text-ink">{group.name}</p>
              <p className="text-sm text-ink-soft">{group.created_at.slice(0, 10)}</p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
