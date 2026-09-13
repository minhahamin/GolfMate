import { useQuery } from '@tanstack/react-query';

import { getCourse, listCourses } from '../api/courses';

export function useCourses() {
  return useQuery({ queryKey: ['courses'], queryFn: listCourses });
}

export function useCourse(courseId: number) {
  return useQuery({
    queryKey: ['courses', courseId],
    queryFn: () => getCourse(courseId),
    enabled: Number.isFinite(courseId),
  });
}
