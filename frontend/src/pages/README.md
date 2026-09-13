# pages/

라우트 하나당 파일 하나. `App.tsx`의 `<Route>`와 1:1로 대응한다.

## 현재

- `Login.tsx` (`/login`) — 로그인 폼. 데모 계정(`demo@golfmate.ai`)으로 바로 체험할 수 있는
  버튼도 있다 (`backend/app/seed_demo_account.py`로 시드됨).
- `Register.tsx` (`/register`) — 회원가입 폼, 성공 시 자동 로그인되어 `/dashboard`로 이동
- `Dashboard.tsx` (`/dashboard`, 보호됨) — 최근 10라운드 통계 요약(평균/베스트 스코어,
  페어웨이·GIR·퍼팅 StatBar, 스코어 추이 Recharts 라인차트). 라운드가 없으면 빈 상태 안내.
- `Coach.tsx` (`/coach`, 보호됨) — AI 코치. 질문(선택) 입력 후 최근 라운드 기반 5개 섹션
  분석(현재 상태/가장 큰 문제/원인/전략/다음 목표)을 보여준다. LLM 호출이라 응답에 몇 초
  걸릴 수 있음을 버튼 텍스트로 안내한다.
- `Profile.tsx` (`/profile`, 보호됨) — 골퍼 프로필 조회/수정 폼 (Dashboard에서 이 페이지로 이동함)
- `Rounds.tsx` (`/rounds`, 보호됨) — 내 라운드 목록
- `RoundNew.tsx` (`/rounds/new`, 보호됨) — 코스 선택 + 기본 정보 + 선택적 18홀 상세 입력
  테이블(체크하면 총타수를 홀 점수 합으로 자동 계산)
- `RoundDetail.tsx` (`/rounds/:id`, 보호됨) — 라운드 정보 + 홀 테이블 + AI 분석(계산 기반) 통계
- `Courses.tsx` (`/courses`, 보호됨) — 골프장 목록
- `CourseDetail.tsx` (`/courses/:id`, 보호됨) — 골프장 정보 + 홀별 파/거리 테이블
- `SystemStatus.tsx` (`/status`) — 백엔드/DB 연결 상태 확인용 (Phase 1에서 만든 인프라 점검
  페이지, 루트 경로에서 `/status`로 이동했다).

## 앞으로 추가될 페이지 (마스터 스펙 §21)

`/caddie`, `/diary`, `/bet`, `/bet/:id`.
