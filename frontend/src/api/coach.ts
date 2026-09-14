import axios from 'axios';

import { apiClient } from './client';
import type { CoachResponse } from '../types/coach';

export async function postCoachAnalysis(question: string): Promise<CoachResponse> {
  // 백엔드 LLM 호출 타임아웃(app/ai/llm/client.py의 timeout=30, 재시도 없음)보다 여유 있게 잡아,
  // 백엔드가 실패해도 상세한 폴백 메시지를 담아 정상 응답(200)할 시간을 준다.
  const { data } = await apiClient.post<CoachResponse>(
    '/api/ai/coach',
    { question },
    { timeout: 35_000 },
  );
  return data;
}

// 백엔드가 응답 자체를 못 준 경우(네트워크/타임아웃/서버 다운)에만 쓰인다 — 백엔드가 응답한
// 경우엔 LLM 실패 사유(무료 사용량 초과 등)가 이미 CoachResponse 텍스트 안에 상세히 담겨온다
// (app/ai/coach/graph.py의 FALLBACK_* 참고).
export function getCoachRequestErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'AI 코치 응답이 35초 안에 오지 않았습니다. 무료 AI 모델이 혼잡할 수 있어요. 잠시 후 다시 시도해주세요.';
    }
    if (!error.response) {
      return '서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해주세요.';
    }
    if (error.response.status >= 500) {
      return '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  return '분석 요청에 실패했습니다. 잠시 후 다시 시도해주세요.';
}
