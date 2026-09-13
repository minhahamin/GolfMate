import { apiClient } from './client';
import type { Course, CourseDetail } from '../types/course';

export async function listCourses(): Promise<Course[]> {
  const { data } = await apiClient.get<Course[]>('/api/courses');
  return data;
}

export async function getCourse(courseId: number): Promise<CourseDetail> {
  const { data } = await apiClient.get<CourseDetail>(`/api/courses/${courseId}`);
  return data;
}
