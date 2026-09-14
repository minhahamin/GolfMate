export interface DiaryListItem {
  id: number;
  round_id: number | null;
  summary: string;
  mood: string;
  created_at: string;
}

export interface Diary extends DiaryListItem {
  round_summary: string | null;
  raw_text: string;
  highlights: string;
  improvement_points: string;
  next_goal: string;
}

export interface DiaryCreatePayload {
  text?: string;
  audioBlob?: Blob;
  roundId?: number;
}
