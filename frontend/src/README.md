# src/

```text
main.tsx   — React Query Provider + BrowserRouter + AuthProvider 설정, 앱 마운트
App.tsx    — 라우트 정의 (Routes/Route), "/"는 로그인 여부에 따라 리다이렉트
pages/     — 라우트 단위 화면
components/— 재사용 UI 컴포넌트 (ProtectedRoute 등)
context/   — 전역 클라이언트 상태 (로그인한 사용자 등)
api/       — axios 클라이언트 및 API 호출 함수
hooks/     — React Query 기반 커스텀 훅
types/     — 백엔드 응답 타입
```

## 데이터 흐름

```text
Page → useXxxQuery (hooks/) → api 함수 (api/) → axios → FastAPI
```

컴포넌트가 axios를 직접 호출하지 않고, 항상 `hooks/`의 React Query 훅을 통해 데이터를 가져온다.
이렇게 하면 로딩/에러/캐싱/재요청 처리가 훅 하나에 모이고, 페이지 컴포넌트는 렌더링에만 집중할 수 있다.
