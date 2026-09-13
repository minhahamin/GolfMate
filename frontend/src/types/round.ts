import type { Course } from './course';

export interface HoleInput {
  hole_number: number;
  par: number;
  score: number;
  putts: number;
  fairway_hit: boolean;
  gir: boolean;
  ob: number;
  bunker: number;
  penalty: number;
}

export type HoleRead = HoleInput;

export interface RoundCreatePayload {
  course_id: number;
  round_date: string; // YYYY-MM-DD
  score?: number;
  weather?: string | null;
  temperature?: number | null;
  wind?: string | null;
  memo?: string | null;
  holes?: HoleInput[];
}

export type RoundUpdatePayload = Partial<Omit<RoundCreatePayload, 'course_id'>>;

export interface RoundListItem {
  id: number;
  course: Course;
  round_date: string;
  score: number;
}

export interface Round extends RoundListItem {
  weather: string | null;
  temperature: number | null;
  wind: string | null;
  memo: string | null;
  holes: HoleRead[];
  created_at: string;
}

export interface RoundAnalysis {
  score: number;
  score_to_par: number | null;
  has_hole_detail: boolean;
  putts_total: number | null;
  putts_average: number | null;
  fairway_hit_rate: number | null;
  gir_rate: number | null;
  ob_count: number | null;
  bunker_count: number | null;
  penalty_count: number | null;
  par3_average: number | null;
  par4_average: number | null;
  par5_average: number | null;
}

export interface RecentRoundPoint {
  round_date: string;
  score: number;
}

export interface StatisticsSummary {
  rounds_count: number;
  average_score: number | null;
  best_score: number | null;
  average_putts: number | null;
  average_fairway_rate: number | null;
  average_gir_rate: number | null;
  recent_rounds: RecentRoundPoint[];
}
