# types/

백엔드 Pydantic 응답 스키마와 대응하는 TypeScript 타입을 정의한다.
백엔드 스키마가 바뀌면 이 폴더도 함께 갱신한다.

## 현재

- `health.ts` — `HealthStatus` (`GET /api/health/db` 응답)
- `auth.ts` — `User`, `AuthResponse`, `GolferProfile`, `GolferProfileUpdate`
- `course.ts` — `Course`(difficulty/green_fee_avg/tags 포함, Phase 7), `CourseHole`, `CourseDetail`
- `round.ts` — `HoleInput`/`HoleRead`, `Round`/`RoundListItem`, `RoundCreatePayload`/
  `RoundUpdatePayload`, `RoundAnalysis`, `StatisticsSummary`
- `coach.ts` — `CoachResponse` (5개 섹션)
- `diary.ts` (Phase 6) — `DiaryListItem`, `Diary`(5개 AI 필드 + round_summary + raw_text),
  `DiaryCreatePayload`(text/audioBlob/roundId — multipart 전송용이라 Round와 달리 camelCase)
- `recommend.ts` (Phase 7) — `CourseRecommendationRequest`, `CourseRecommendation`(Course +
  reason), `CourseRecommendationResponse`
- `caddie.ts` (Phase 8) — `CaddieRequest`, `CaddieResponse`(weather_summary + 3개 섹션)
- `group.ts` (Phase 9) — `GroupRead`, `GroupMember`, `GroupDetail`(GroupRead + members)
- `bet.ts` (Phase 9) — `BetCreatePayload`(scores: user_id -> score), `BetResult`,
  `BetListItem`/`Bet`
