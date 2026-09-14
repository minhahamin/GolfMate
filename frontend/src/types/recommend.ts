import type { Course } from './course';

export interface CourseRecommendationRequest {
  region?: string;
  difficulty?: string;
  max_budget?: number;
  preference_text?: string;
}

export interface CourseRecommendation {
  course: Course;
  reason: string;
}

export interface CourseRecommendationResponse {
  summary: string;
  recommendations: CourseRecommendation[];
}
