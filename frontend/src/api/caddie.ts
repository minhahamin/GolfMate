import axios from 'axios';

import { apiClient } from './client';
import type { CaddieRequest, CaddieResponse } from '../types/caddie';

export async function postCaddieAdvice(payload: CaddieRequest): Promise<CaddieResponse> {
  // 날씨 조회(Open-Meteo) + LLM 호출을 순차로 거치므로 Coach(35초)보다 여유 있게 잡는다.
  const { data } = await apiClient.post<CaddieResponse>('/api/ai/caddie', payload, {
    timeout: 45_000,
  });
  return data;
}

export function getCaddieRequestErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'AI 캐디 응답이 45초 안에 오지 않았습니다. 잠시 후 다시 시도해주세요.';
    }
    if (!error.response) {
      return '서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해주세요.';
    }
    if (error.response.status === 404) {
      return '골프장 또는 홀 정보를 찾을 수 없습니다.';
    }
    if (error.response.status >= 500) {
      return '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  return '캐디 요청에 실패했습니다. 잠시 후 다시 시도해주세요.';
}
