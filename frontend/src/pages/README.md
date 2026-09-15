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
  걸릴 수 있음을 버튼 텍스트로 안내한다. 결과 위 "🔊 읽어주기"(`SpeakButton`)로 소리 내어
  들을 수 있다.
- `Profile.tsx` (`/profile`, 보호됨) — 골퍼 프로필 조회/수정 폼 (Dashboard에서 이 페이지로 이동함)
- `Rounds.tsx` (`/rounds`, 보호됨) — 내 라운드 목록
- `RoundNew.tsx` (`/rounds/new`, 보호됨) — 코스 선택 + 기본 정보 + 선택적 18홀 상세 입력
  테이블(체크하면 총타수를 홀 점수 합으로 자동 계산)
- `RoundDetail.tsx` (`/rounds/:id`, 보호됨) — 라운드 정보 + 홀 테이블 + AI 분석(계산 기반) 통계
- `Courses.tsx` (`/courses`, 보호됨) — 골프장 목록(난이도/평균 그린피 포함), AI 추천받기 버튼
- `CourseRecommend.tsx` (`/courses/recommend`, 보호됨, Phase 7) — 지역/난이도/예산/선호
  텍스트 조건 입력 → AI가 실제 후보 중 최대 3곳을 순위/이유와 함께 추천
- `CourseDetail.tsx` (`/courses/:id`, 보호됨) — 골프장 정보 + 난이도/그린피/태그 + 홀별 파/거리 테이블
- `Diary.tsx` (`/diary`, 보호됨) — 내 AI 일기 목록 (날짜/기분/요약 미리보기)
- `DiaryNew.tsx` (`/diary/new`, 보호됨) — 텍스트 입력 또는 마이크 녹음(`useAudioRecorder`)으로
  일기 작성, 선택적 라운드 드롭다운(비워두면 AI가 최근 라운드 중에서 자동 매칭)
- `DiaryDetail.tsx` (`/diary/:id`, 보호됨) — AI가 정리한 5개 필드(기분/하이라이트/개선점/
  다음목표/요약)와 원문, 연결된 라운드 정보. "AI 정리" 섹션에 "🔊 읽어주기" 버튼이 있다.
- `Caddie.tsx` (`/caddie`, 보호됨, Phase 8) — 골프장+홀 선택 → 실시간 날씨(Open-Meteo)를
  반영한 홀공략/위험요소/클럽전략 3개 섹션을 보여준다. 라운드 중 손이 바쁠 때를 고려해
  "🔊 읽어주기"로 결과 전체(날씨+3섹션)를 들을 수 있다.
- `Groups.tsx` (`/groups`, 보호됨, Phase 9) — 내가 속한 모임 목록 + 새 모임 생성 폼
- `GroupDetail.tsx` (`/groups/:id`, 보호됨, Phase 9) — 멤버 목록(그룹장만 이메일로 멤버
  추가/제거 가능, 본인은 언제든 탈퇴 가능) + 내기 기록 목록
- `BetNew.tsx` (`/groups/:id/bets/new`, 보호됨, Phase 9) — 내기 이름/날짜/골프장/타당 금액 +
  그룹 멤버별 스코어 입력(2명 이상) → 제출 시 서버가 정산 계산
- `BetDetail.tsx` (`/bets/:id`, 보호됨, Phase 9) — 참가자별 스코어/정산 금액 테이블 +
  "코멘터리 받기" 버튼(AI가 이미 계산된 결과를 설명)
- `SystemStatus.tsx` (`/status`) — 백엔드/DB 연결 상태 확인용 (Phase 1에서 만든 인프라 점검
  페이지, 루트 경로에서 `/status`로 이동했다).
