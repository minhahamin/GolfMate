import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { createDiary, deleteDiary, getDiary, listDiaries } from '../api/diary';

const DIARIES_KEY = ['diaries'];

export function useDiaries() {
  return useQuery({ queryKey: DIARIES_KEY, queryFn: listDiaries });
}

export function useDiary(diaryId: number) {
  return useQuery({
    queryKey: [...DIARIES_KEY, diaryId],
    queryFn: () => getDiary(diaryId),
    enabled: Number.isFinite(diaryId),
  });
}

export function useCreateDiary() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: createDiary,
    onSuccess: (diary) => {
      queryClient.invalidateQueries({ queryKey: DIARIES_KEY });
      navigate(`/diary/${diary.id}`);
    },
  });
}

export function useDeleteDiary() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: deleteDiary,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DIARIES_KEY });
      navigate('/diary');
    },
  });
}
