import { useMutation } from '@tanstack/react-query';

import { postCourseRecommendation } from '../api/recommend';
import type { CourseRecommendationRequest } from '../types/recommend';

export function useCourseRecommendation() {
  return useMutation({
    mutationFn: (payload: CourseRecommendationRequest) => postCourseRecommendation(payload),
  });
}
