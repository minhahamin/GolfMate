export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface GolferProfile {
  id: number;
  user_id: number;
  handicap: number | null;
  average_score: number | null;
  driver_distance: number | null;
  iron_distance: number | null;
  putting_average: number | null;
  fairway_percentage: number | null;
  gir_percentage: number | null;
  preferred_tee: string | null;
  goal_score: number | null;
  created_at: string;
}

export type GolferProfileUpdate = Partial<
  Omit<GolferProfile, 'id' | 'user_id' | 'created_at'>
>;
