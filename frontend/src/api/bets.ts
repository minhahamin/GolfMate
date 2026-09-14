import axios from 'axios';

import { apiClient } from './client';
import type { Bet, BetCreatePayload, BetListItem } from '../types/bet';

export async function listBets(groupId: number): Promise<BetListItem[]> {
  const { data } = await apiClient.get<BetListItem[]>(`/api/groups/${groupId}/bets`);
  return data;
}

export async function createBet(groupId: number, payload: BetCreatePayload): Promise<Bet> {
  const { data } = await apiClient.post<Bet>(`/api/groups/${groupId}/bets`, payload);
  return data;
}

export async function getBet(betId: number): Promise<Bet> {
  const { data } = await apiClient.get<Bet>(`/api/bets/${betId}`);
  return data;
}

export async function postBetCommentary(betId: number): Promise<{ commentary: string }> {
  const { data } = await apiClient.post<{ commentary: string }>(
    '/api/ai/bet-commentary',
    { bet_id: betId },
    { timeout: 35_000 },
  );
  return data;
}

export function getBetCommentaryErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'AI 코멘터리 응답이 35초 안에 오지 않았습니다. 잠시 후 다시 시도해주세요.';
    }
    if (!error.response) {
      return '서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해주세요.';
    }
    if (error.response.status >= 500) {
      return '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  return '코멘터리 요청에 실패했습니다. 잠시 후 다시 시도해주세요.';
}
