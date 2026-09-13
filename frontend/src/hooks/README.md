# hooks/

`@tanstack/react-query` 기반 커스텀 훅. 컴포넌트는 이 훅을 통해서만 서버 데이터를 가져온다.

## 현재

- `useHealthCheck.ts` — `/api/health/db`를 10초마다 폴링해 연결 상태를 확인한다.

Phase 2+에서 `useAuth`, `useRounds`, `useCoachAnalysis` 등이 같은 패턴으로 추가된다.
