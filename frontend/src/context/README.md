# context/

전역으로 공유해야 하는 클라이언트 상태를 React Context로 둔다. 서버 데이터 캐싱은
`hooks/`(React Query)가 담당하고, 여기는 "현재 로그인한 사용자가 누구인지" 같은
앱 전역 상태만 다룬다.

- `AuthContext.tsx` — 로그인한 `user`, 로딩 상태, `loginWithAuthResponse()`, `logout()`.
  앱 시작 시 `localStorage`에 저장된 토큰으로 `/api/users/me`를 호출해 로그인 상태를
  복원한다. 토큰 저장/조회 자체는 `api/client.ts`에 있고, 여기서는 그 결과로 사용자 상태만
  관리한다.

`useAuth()` 훅으로 어디서든 로그인 상태에 접근한다 (`AuthProvider` 바깥에서 호출하면 에러).
