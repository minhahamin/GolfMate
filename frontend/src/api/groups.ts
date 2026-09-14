import { apiClient } from './client';
import type { GroupDetail, GroupRead } from '../types/group';

export async function listGroups(): Promise<GroupRead[]> {
  const { data } = await apiClient.get<GroupRead[]>('/api/groups');
  return data;
}

export async function getGroup(groupId: number): Promise<GroupDetail> {
  const { data } = await apiClient.get<GroupDetail>(`/api/groups/${groupId}`);
  return data;
}

export async function createGroup(name: string): Promise<GroupDetail> {
  const { data } = await apiClient.post<GroupDetail>('/api/groups', { name });
  return data;
}

export async function addGroupMember(groupId: number, email: string): Promise<GroupDetail> {
  const { data } = await apiClient.post<GroupDetail>(`/api/groups/${groupId}/members`, { email });
  return data;
}

export async function removeGroupMember(groupId: number, userId: number): Promise<void> {
  await apiClient.delete(`/api/groups/${groupId}/members/${userId}`);
}
