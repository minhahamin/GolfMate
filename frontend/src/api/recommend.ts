import axios from 'axios';

import { apiClient } from './client';
import type { CourseRecommendationRequest, CourseRecommendationResponse } from '../types/recommend';

export async function postCourseRecommendation(
  payload: CourseRecommendationRequest,
): Promise<CourseRecommendationResponse> {
  const { data } = await apiClient.post<CourseRecommendationResponse>(
    '/api/ai/recommend-courses',
    payload,
    { timeout: 35_000 },
  );
  return data;
}

export function getRecommendRequestErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'AI 추천 응답이 35초 안에 오지 않았습니다. 잠시 후 다시 시도해주세요.';
    }
    if (!error.response) {
      return '서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해주세요.';
    }
    if (error.response.status >= 500) {
      return '서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    }
  }
  return '추천 요청에 실패했습니다. 잠시 후 다시 시도해주세요.';
}
