import { apiClient } from './client';
import type { GolferProfile, GolferProfileUpdate, User } from '../types/auth';

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/api/users/me');
  return data;
}

export async function getMyProfile(): Promise<GolferProfile> {
  const { data } = await apiClient.get<GolferProfile>('/api/users/me/profile');
  return data;
}

export async function updateMyProfile(payload: GolferProfileUpdate): Promise<GolferProfile> {
  const { data } = await apiClient.put<GolferProfile>('/api/users/me/profile', payload);
  return data;
}
