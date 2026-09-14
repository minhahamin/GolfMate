import { useState, type FormEvent } from 'react';

import { getDiaryRequestErrorMessage } from '../api/diary';
import Layout from '../components/Layout';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useCreateDiary } from '../hooks/useDiary';
import { useRounds } from '../hooks/useRounds';

const fieldClass =
  'mt-1.5 w-full border border-ink/20 bg-transparent px-3 py-2 text-ink outline-none focus:border-ink';

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function DiaryNew() {
  const [text, setText] = useState('');
  const [roundId, setRoundId] = useState('');

  const { data: rounds } = useRounds();
  const recorder = useAudioRecorder();
  const createDiary = useCreateDiary();

  const hasContent = text.trim().length > 0 || recorder.audioBlob !== null;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!hasContent) return;

    createDiary.mutate({
      text: text.trim() || undefined,
      audioBlob: recorder.audioBlob ?? undefined,
      roundId: roundId ? Number(roundId) : undefined,
    });
  }

  return (
    <Layout>
      <h1 className="font-display text-3xl text-ink">새 일기 쓰기</h1>
      <p className="mt-1 text-sm text-ink-soft">
        오늘 라운드 소감을 글로 쓰거나 음성으로 녹음해주세요. AI가 정리해드려요.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <section className="border border-ink/15 p-6">
          <label className="block text-sm text-ink-soft">
            연결할 라운드 (선택 — 비워두면 AI가 자동으로 찾아봐요)
            <select value={roundId} onChange={(e) => setRoundId(e.target.value)} className={fieldClass}>
              <option value="">자동 매칭</option>
              {rounds?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.round_date} {r.course.name} ({r.score}타)
                </option>
              ))}
            </select>
          </label>

          <label className="mt-4 block text-sm text-ink-soft">
            텍스트로 쓰기
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="예: 오늘은 드라이버가 잘 맞았는데 퍼팅이 아쉬웠다..."
              rows={5}
              maxLength={2000}
              className={fieldClass}
            />
          </label>

          <div className="mt-4">
            <p className="text-sm text-ink-soft">또는 음성으로 녹음하기</p>
            <div className="mt-1.5 flex items-center gap-4">
              {!recorder.isRecording ? (
                <button
                  type="button"
                  onClick={recorder.start}
                  className="border border-ink/20 px-4 py-2 text-sm text-ink transition hover:bg-paper-2"
                >
                  🎙 녹음 시작
                </button>
              ) : (
                <button
                  type="button"
                  onClick={recorder.stop}
                  className="border border-flag bg-flag/10 px-4 py-2 text-sm text-flag transition hover:bg-flag/20"
                >
                  ■ 정지 ({formatDuration(recorder.durationSec)})
                </button>
              )}

              {recorder.audioBlob && !recorder.isRecording && (
                <div className="flex items-center gap-3">
                  <audio controls src={URL.createObjectURL(recorder.audioBlob)} className="h-9" />
                  <button
                    type="button"
                    onClick={recorder.reset}
                    className="text-sm text-ink-soft underline underline-offset-2"
                  >
                    다시 녹음
                  </button>
                </div>
              )}
            </div>
            {recorder.error && <p className="mt-2 text-sm text-flag">{recorder.error}</p>}
          </div>
        </section>

        {createDiary.isError && (
          <p className="text-sm text-flag">{getDiaryRequestErrorMessage(createDiary.error)}</p>
        )}

        <button
          type="submit"
          disabled={createDiary.isPending || !hasContent}
          className="bg-flag px-6 py-2.5 font-medium text-paper transition hover:bg-flag-deep disabled:opacity-50"
        >
          {createDiary.isPending ? '정리 중... (최대 1분 정도 걸려요)' : '일기 저장'}
        </button>
      </form>
    </Layout>
  );
}
