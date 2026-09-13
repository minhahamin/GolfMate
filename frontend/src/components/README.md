# components/

여러 페이지에서 재사용하는 UI 조각을 둔다.

## 현재

- `ProtectedRoute.tsx` — 로그인하지 않은 사용자가 보호된 라우트(`/dashboard` 등)에 접근하면
  `/login`으로 리다이렉트한다. `useAuth()`의 로딩 상태가 끝날 때까지는 아무것도 렌더링하지
  않는다 (로그인 상태 확인 전에 잠깐 `/login`으로 튕기는 깜빡임 방지).

Phase 3+에서 `Layout`(공통 네비게이션), `StatCard`, `ProgressBar`(§22의 AI 분석 시각화 바),
`AiAnalysisCard` 같은 컴포넌트가 이 폴더에 추가될 예정이다.
