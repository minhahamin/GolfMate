# types/

백엔드 Pydantic 응답 스키마와 대응하는 TypeScript 타입을 정의한다.
백엔드 스키마가 바뀌면 이 폴더도 함께 갱신한다.

## 현재

- `health.ts` — `HealthStatus` (`GET /api/health/db` 응답)
- `auth.ts` — `User`, `AuthResponse`, `GolferProfile`, `GolferProfileUpdate`
- `course.ts` — `Course`, `CourseHole`, `CourseDetail`
- `round.ts` — `HoleInput`/`HoleRead`, `Round`/`RoundListItem`, `RoundCreatePayload`/
  `RoundUpdatePayload`, `RoundAnalysis`, `StatisticsSummary`
