# components/

여러 페이지에서 재사용하는 UI 조각을 둔다.

## 현재

- `ProtectedRoute.tsx` — 로그인하지 않은 사용자가 보호된 라우트(`/dashboard` 등)에 접근하면
  `/login`으로 리다이렉트한다. `useAuth()`의 로딩 상태가 끝날 때까지는 아무것도 렌더링하지
  않는다 (로그인 상태 확인 전에 잠깐 `/login`으로 튕기는 깜빡임 방지).
- `AuthHero.tsx` — 로그인/회원가입 페이지 좌측의 히어로 패널(골프 캐디 토끼 마스코트 이미지 +
  태그라인). 데스크톱(`lg` 이상)에서만 보이고 모바일에서는 숨겨 폼에 집중하게 한다.
- `Layout.tsx` — 로그인 이후 페이지(Dashboard/Coach/Rounds/Courses/Profile) 공통 상단
  네비게이션 + 워드마크(깃발 아이콘 + serif 로고).
- `StatBar.tsx` — §22의 "████████░░" 스타일 막대. GIR/페어웨이/퍼팅 등 비율 지표를 시각화한다.
- `SpeakButton.tsx` (TTS) — `useTextToSpeech`를 감싼 "🔊 읽어주기" 토글 버튼. `text` prop만
  받아 재생/중지를 알아서 전환한다. Coach/Caddie/DiaryDetail에서 AI 분석 결과를 읽어주는 데
  쓴다. 브라우저가 Web Speech API를 지원하지 않으면 아무것도 렌더링하지 않는다.
