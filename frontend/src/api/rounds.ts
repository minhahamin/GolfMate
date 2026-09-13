import { apiClient } from './client';
import type {
  Round,
  RoundAnalysis,
  RoundCreatePayload,
  RoundListItem,
  RoundUpdatePayload,
  StatisticsSummary,
} from '../types/round';

export async function listRounds(): Promise<RoundListItem[]> {
  const { data } = await apiClient.get<RoundListItem[]>('/api/rounds');
  return data;
}

export async function createRound(payload: RoundCreatePayload): Promise<Round> {
  const { data } = await apiClient.post<Round>('/api/rounds', payload);
  return data;
}

export async function getRound(roundId: number): Promise<Round> {
  const { data } = await apiClient.get<Round>(`/api/rounds/${roundId}`);
  return data;
}

export async function updateRound(roundId: number, payload: RoundUpdatePayload): Promise<Round> {
  const { data } = await apiClient.put<Round>(`/api/rounds/${roundId}`, payload);
  return data;
}

export async function deleteRound(roundId: number): Promise<void> {
  await apiClient.delete(`/api/rounds/${roundId}`);
}

export async function getRoundAnalysis(roundId: number): Promise<RoundAnalysis> {
  const { data } = await apiClient.get<RoundAnalysis>(`/api/rounds/${roundId}/analysis`);
  return data;
}

export async function getStatisticsSummary(limit = 10): Promise<StatisticsSummary> {
  const { data } = await apiClient.get<StatisticsSummary>('/api/rounds/statistics/summary', {
    params: { limit },
  });
  return data;
}
