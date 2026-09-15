import { useCallback, useEffect, useState } from 'react';

export const isSpeechSynthesisSupported =
  typeof window !== 'undefined' && 'speechSynthesis' in window;

function pickKoreanVoice(): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis.getVoices();
  return voices.find((voice) => voice.lang.startsWith('ko')) ?? null;
}

// 브라우저 내장 Web Speech API(TTS)를 감싼 훅. useAudioRecorder.ts와 같은 이유로 서버 데이터가
// 아니라 브라우저 API를 다뤄서 react-query를 쓰지 않는다. 서버 TTS(GPU/과금 필요) 없이
// 클라이언트에서만 합성해, 이 프로젝트의 "과금 없이" 원칙을 음성 출력에도 그대로 적용한다.
export function useTextToSpeech() {
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    if (!isSpeechSynthesisSupported) return;
    // 크롬 계열은 getVoices()를 한 번 호출해야 voiceschanged가 뒤늦게 발생하며 목록이 찬다.
    window.speechSynthesis.getVoices();
  }, []);

  const stop = useCallback(() => {
    if (!isSpeechSynthesisSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (!isSpeechSynthesisSupported || !text.trim()) return;

    window.speechSynthesis.cancel(); // 읽던 중이면 먼저 끊고 새로 시작한다

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    utterance.voice = pickKoreanVoice();
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  useEffect(() => stop, [stop]); // 페이지 이동 등으로 언마운트되면 읽던 것을 끊는다

  return { isSupported: isSpeechSynthesisSupported, isSpeaking, speak, stop };
}
