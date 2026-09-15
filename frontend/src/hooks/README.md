# hooks/

`@tanstack/react-query` 기반 커스텀 훅. 컴포넌트는 이 훅을 통해서만 서버 데이터를 가져온다.
로그인 여부 같은 전역 클라이언트 상태는 `context/AuthContext.tsx`(`useAuth()`)가 담당한다.

## 현재

- `useHealthCheck.ts` — `/api/health/db`를 10초마다 폴링해 연결 상태를 확인한다.
- `useLogin.ts` / `useRegister.ts` — 로그인/회원가입 mutation. 성공 시
  `AuthContext.loginWithAuthResponse()`를 호출해 토큰 저장과 사용자 상태 갱신을 한 번에 한다.
- `useMyProfile.ts` — 내 골퍼 프로필 조회(`useQuery`, 로그인 상태일 때만 `enabled`)와
  수정(`useUpdateMyProfile`, 성공 시 캐시 직접 갱신).
- `useCourses.ts` — `useCourses`(목록), `useCourse(id)`(상세, 홀 목록 포함).
- `useRounds.ts` — `useRounds`(목록), `useRound(id)`(상세), `useCreateRound`(성공 시 상세
  페이지로 이동), `useUpdateRound(id)`, `useDeleteRound`(성공 시 목록으로 이동).
- `useRoundAnalysis.ts` — 라운드 하나의 통계(`/rounds/{id}/analysis`).
- `useStatisticsSummary.ts` — 최근 N라운드 집계 통계 (로그인 상태일 때만 `enabled`), Dashboard가 쓴다.
- `useCoach.ts` — AI 코치 분석 요청(`useMutation`). LLM 호출이라 몇 초 걸릴 수 있다
  (`api/coach.ts`가 타임아웃을 30초로 늘려서 호출한다).
- `useDiary.ts` (Phase 6) — `useDiaries`(목록), `useDiary(id)`(상세), `useCreateDiary`(성공 시
  상세 페이지로 이동), `useDeleteDiary`(성공 시 목록으로 이동) — `useRounds.ts`와 동일한 패턴.
- `useAudioRecorder.ts` (Phase 6) — `MediaRecorder` 기반 녹음 훅.
  `{ isRecording, durationSec, audioBlob, error, start(), stop(), reset() }`을 반환한다.
  이 프로젝트에 처음 들어간 오디오 캡처라 서버 데이터 훅이 아니라 브라우저 API를 감싼
  훅이다 (react-query 미사용).
- `useRecommend.ts` (Phase 7) — `useCourseRecommendation`(`useMutation`) — `useCoach.ts`와
  동일한 패턴.
- `useCaddie.ts` (Phase 8) — `useCaddie`(`useMutation`) — `useCoach.ts`와 동일한 패턴.
- `useGroups.ts` (Phase 9) — `useGroups`(목록), `useGroup(id)`(상세), `useCreateGroup`(성공 시
  상세 페이지로 이동), `useAddGroupMember(groupId)`, `useRemoveGroupMember(groupId)`.
- `useBets.ts` (Phase 9) — `useBets(groupId)`(목록), `useBet(id)`(상세),
  `useCreateBet(groupId)`(성공 시 상세 페이지로 이동) — `useRounds.ts`와 동일한 패턴.
- `useBetCommentary.ts` (Phase 9) — `useBetCommentary`(`useMutation`) — `useCoach.ts`와
  동일한 패턴.

Phase 10(Langfuse)은 새 프론트엔드 훅이 필요 없다 — 백엔드 트레이싱만 추가된다.

- `useTextToSpeech.ts` (TTS) — 브라우저 내장 Web Speech API(`speechSynthesis`)를 감싼 훅.
  `useAudioRecorder.ts`와 같은 이유로 서버 데이터가 아니라 브라우저 API를 다뤄 react-query를
  쓰지 않는다. `{ isSupported, isSpeaking, speak(text), stop() }`을 반환하고, 서버 TTS
  없이 클라이언트에서만 합성해 과금이 발생하지 않는다.
