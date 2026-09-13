import { apiClient } from './client';
import type { CoachResponse } from '../types/coach';

export async function postCoachAnalysis(question: string): Promise<CoachResponse> {
  // LLM 호출은 몇 초 이상 걸릴 수 있어, apiClient의 기본 타임아웃(5초)보다 넉넉하게 잡는다.
  const { data } = await apiClient.post<CoachResponse>(
    '/api/ai/coach',
    { question },
    { timeout: 30_000 },
  );
  return data;
}
