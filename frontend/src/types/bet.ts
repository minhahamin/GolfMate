export interface BetCreatePayload {
  title: string;
  bet_date: string; // YYYY-MM-DD
  course_name: string;
  stake_per_stroke: number;
  scores: Record<number, number>; // user_id -> score
}

export interface BetResult {
  user_id: number;
  name: string;
  score: number;
  payout_amount: number;
}

export interface BetListItem {
  id: number;
  title: string;
  bet_date: string;
  course_name: string;
  created_at: string;
}

export interface Bet extends BetListItem {
  group_id: number;
  stake_per_stroke: number;
  results: BetResult[];
}
