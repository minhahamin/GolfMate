import { useCallback, useEffect, useRef, useState } from 'react';

function pickMimeType(): string {
  const candidates = ['audio/webm', 'audio/mp4', 'audio/ogg'];
  for (const type of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return '';
}

// 녹음 시작/정지, 경과 시간, 결과 Blob을 다루는 훅. 이 프로젝트에 처음 들어가는 오디오
// 캡처라 참고할 기존 패턴이 없어 신규 작성했다. 원본 오디오는 전사 후 서버에서 폐기되므로
// (app/ai/stt/transcriber.py), 여기서도 재녹음 시 이전 Blob을 그냥 버린다.
export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [durationSec, setDurationSec] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(async () => {
    setError(null);
    setAudioBlob(null);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = pickMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType || 'audio/webm' });
        setAudioBlob(blob);
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      recorder.start();
      setIsRecording(true);
      setDurationSec(0);
      intervalRef.current = setInterval(() => setDurationSec((sec) => sec + 1), 1000);
    } catch {
      setError('마이크를 사용할 수 없습니다. 브라우저 권한을 확인해주세요.');
    }
  }, []);

  const stop = useCallback(() => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    stopTimer();
  }, [stopTimer]);

  const reset = useCallback(() => {
    setAudioBlob(null);
    setDurationSec(0);
    setError(null);
  }, []);

  useEffect(() => stopTimer, [stopTimer]);

  return { isRecording, durationSec, audioBlob, error, start, stop, reset };
}
