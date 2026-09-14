import axios from 'axios';

import { apiClient } from './client';
import type { Diary, DiaryCreatePayload, DiaryListItem } from '../types/diary';

export async function listDiaries(): Promise<DiaryListItem[]> {
  const { data } = await apiClient.get<DiaryListItem[]>('/api/diaries');
  return data;
}

export async function getDiary(diaryId: number): Promise<Diary> {
  const { data } = await apiClient.get<Diary>(`/api/diaries/${diaryId}`);
  return data;
}

export async function createDiary(payload: DiaryCreatePayload): Promise<Diary> {
  const formData = new FormData();
  if (payload.text) formData.append('text', payload.text);
  if (payload.audioBlob) formData.append('audio', payload.audioBlob, 'diary.webm');
  if (payload.roundId) formData.append('round_id', String(payload.roundId));

  // 백엔드가 음성이면 STT(로컬 whisper) + LLM 정리를 순차로 거치므로, Coach(35초)보다
  // 여유 있게 잡는다 (app/ai/stt/transcriber.py + app/ai/diary/graph.py 참고).
  const { data } = await apiClient.post<Diary>('/api/diaries', formData, { timeout: 60_000 });
  return data;
}

export async function deleteDiary(diaryId: number): Promise<void> {
  await apiClient.delete(`/api/diaries/${diaryId}`);
}

// 백엔드가 응답 자체를 못 준 경우(네트워크/타임아웃/서버 다운)에만 쓰인다 — 백엔드가 응답한
// 경우엔 LLM 실패 사유가 이미 Diary 텍스트 안에 담겨온다(app/ai/diary/graph.py의 FALLBACK_* 참고).
export function getDiaryRequestErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'AI 일기 정리 응답이 60초 안에 오지 않았습니다. 잠시 후 다시 시도해주세요.';
    }
    if (!error.response) {
      return '서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해주세요.';
    }
    if (error.response.status === 422) {
      return '음성을 인식하지 못했습니다. 다시 녹음하거나 텍스트로 입력해주세요.';
    }
    if (error.response.status === 400) {
      return '일기 내용을 입력하거나 음성을 녹음해주세요.';
    }
    if (error.response.status >= 500) {
      return '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  return '일기 저장에 실패했습니다. 잠시 후 다시 시도해주세요.';
}
