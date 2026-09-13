# api/

- `client.ts` — axios 인스턴스. `baseURL`은 `VITE_API_BASE_URL` 환경변수에서만 읽고
  코드에 하드코딩하지 않는다.

Phase 2부터 도메인별 API 함수 파일(`auth.ts`, `rounds.ts`, `coach.ts` 등)이 추가되며,
각 파일은 `apiClient`를 이용해 실제 HTTP 호출만 담당한다 (에러 처리/캐싱은 `hooks/`에서).
JWT 인증이 추가되면 `client.ts`에 요청 인터셉터로 Authorization 헤더를 붙인다.
