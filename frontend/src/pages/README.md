# pages/

라우트 하나당 파일 하나. `App.tsx`의 `<Route>`와 1:1로 대응한다.

## 현재

- `Login.tsx` (`/login`) — 로그인 폼
- `Register.tsx` (`/register`) — 회원가입 폼, 성공 시 자동 로그인되어 `/dashboard`로 이동
- `Dashboard.tsx` (`/dashboard`, 보호됨) — 로그인한 사용자 정보 + 골퍼 프로필 조회/수정 폼.
  라운드 데이터가 아직 없어 값은 직접 입력한다 (Phase 3부터 라운드 통계로 대체 예정).
- `SystemStatus.tsx` (`/status`) — 백엔드/DB 연결 상태 확인용 (Phase 1에서 만든 인프라 점검
  페이지, 루트 경로에서 `/status`로 이동했다).

## 앞으로 추가될 페이지 (마스터 스펙 §21)

`/profile`, `/rounds`, `/rounds/new`, `/rounds/:id`, `/coach`, `/caddie`, `/courses`,
`/courses/:id`, `/diary`, `/bet`, `/bet/:id`.
