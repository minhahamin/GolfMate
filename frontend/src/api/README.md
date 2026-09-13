# api/

- `client.ts` — axios 인스턴스. `baseURL`은 `VITE_API_BASE_URL` 환경변수에서만 읽고
  코드에 하드코딩하지 않는다. JWT를 `localStorage`에 저장/조회/삭제하는 함수
  (`getStoredToken`/`setStoredToken`/`clearStoredToken`)도 여기 있다 — 요청 인터셉터가
  모든 요청에 `Authorization` 헤더를 자동으로 붙이고, 응답 인터셉터가 401을 받으면 토큰을
  지운다.
- `auth.ts` — `register()`, `login()` (둘 다 `AuthResponse` 반환)
- `users.ts` — `getMe()`, `getMyProfile()`, `updateMyProfile()`
- `courses.ts` — `listCourses()`, `getCourse(id)`
- `rounds.ts` — `listRounds()`, `createRound()`, `getRound(id)`, `updateRound(id)`,
  `deleteRound(id)`, `getRoundAnalysis(id)`, `getStatisticsSummary(limit)`
- `coach.ts` — `postCoachAnalysis(question)`. LLM 호출이라 몇 초 이상 걸릴 수 있어
  `apiClient`의 기본 타임아웃(5초)을 30초로 오버라이드해서 호출한다 — 새로 LLM을 부르는
  API를 추가할 때는 이 패턴을 따른다.

각 파일은 `apiClient`를 이용해 실제 HTTP 호출만 담당한다 (에러 처리/캐싱은 `hooks/`에서,
로그인 상태 반영은 `context/AuthContext.tsx`에서).
