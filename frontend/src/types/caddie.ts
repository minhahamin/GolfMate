export interface CaddieRequest {
  course_id: number;
  hole_number: number;
  question?: string;
}

export interface CaddieResponse {
  weather_summary: string | null;
  hole_analysis: string;
  risk_analysis: string;
  club_strategy: string;
}
