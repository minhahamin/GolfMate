import { useTextToSpeech } from '../hooks/useTextToSpeech';

// AI 분석 결과를 소리 내어 읽어주는 토글 버튼(Phase 10, Web Speech API). 브라우저가 TTS를
// 지원하지 않으면 아무것도 렌더링하지 않는다 — 과금 없는 브라우저 내장 기능이라 지원 안 될
// 때 대체 수단을 두지 않는다.
export default function SpeakButton({ text }: { text: string }) {
  const { isSupported, isSpeaking, speak, stop } = useTextToSpeech();

  if (!isSupported) return null;

  return (
    <button
      type="button"
      onClick={() => (isSpeaking ? stop() : speak(text))}
      className="shrink-0 border border-ink/20 px-3 py-1.5 text-xs text-ink-soft transition hover:border-ink hover:text-ink"
    >
      {isSpeaking ? '⏹ 중지' : '🔊 읽어주기'}
    </button>
  );
}
