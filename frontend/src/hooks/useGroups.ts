import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { addGroupMember, createGroup, getGroup, listGroups, removeGroupMember } from '../api/groups';

const GROUPS_KEY = ['groups'];

export function useGroups() {
  return useQuery({ queryKey: GROUPS_KEY, queryFn: listGroups });
}

export function useGroup(groupId: number) {
  return useQuery({
    queryKey: [...GROUPS_KEY, groupId],
    queryFn: () => getGroup(groupId),
    enabled: Number.isFinite(groupId),
  });
}

export function useCreateGroup() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (name: string) => createGroup(name),
    onSuccess: (group) => {
      queryClient.invalidateQueries({ queryKey: GROUPS_KEY });
      navigate(`/groups/${group.id}`);
    },
  });
}

export function useAddGroupMember(groupId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (email: string) => addGroupMember(groupId, email),
    onSuccess: (group) => {
      queryClient.setQueryData([...GROUPS_KEY, groupId], group);
    },
  });
}

export function useRemoveGroupMember(groupId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => removeGroupMember(groupId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...GROUPS_KEY, groupId] });
    },
  });
}
