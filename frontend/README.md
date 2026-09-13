# GolfMate AI — Frontend

React + TypeScript + Vite + Tailwind CSS. React Query로 서버 상태를 관리하고,
React Router로 화면을 나눈다.

## 로컬 실행 (Docker 없이)

```bash
cd frontend
npm install
cp .env.example .env     # VITE_API_BASE_URL 확인
npm run dev
```

Vite 8은 Node.js 20.19+ / 22.12+를 요구한다. 더 낮은 버전(예: 20.16)에서도 대체로 동작하지만,
`npm install` 후 `vite build`가 `Cannot find native binding` 에러를 내면 npm의 알려진
optional-dependency 버그([npm/cli#4828](https://github.com/npm/cli/issues/4828))다. 아래로 해결한다.

```bash
rm -rf node_modules package-lock.json
npm install
```

그래도 안 되면 누락된 플랫폼 바이너리를 직접 설치한다 (Windows x64 예시):

```bash
npm install --no-save @rolldown/binding-win32-x64-msvc
```

Docker Compose로 실행하면 `node:20-alpine` 이미지가 최신 20.x 패치를 쓰므로 이 문제를 겪지 않는다.

`http://localhost:5180` 접속 시 로그인 여부에 따라 `/login` 또는 `/dashboard`로 이동한다.
Phase 1의 인프라 점검용 페이지는 `/status`에 남아있다.

## Docker Compose로 실행

프로젝트 루트에서 `docker compose up --build` 실행 후 동일한 주소로 접속한다.

## 트러블슈팅: "연결 실패"가 뜰 때

`SystemStatus` 페이지가 연결 실패를 보여준다면 대부분 포트 충돌이다. 로컬에 다른 프로젝트가
Vite(5173)나 FastAPI(8000) 기본 포트를 이미 쓰고 있으면, 브라우저가 `localhost`를
IPv6(`::1`)로 먼저 해석해 엉뚱한 서버로 연결될 수 있다. GolfMate는 기본적으로 8010/5180
포트를 써서 이 문제를 피하지만, 그래도 겹친다면 `.env`의 `BACKEND_PORT`/`FRONTEND_PORT`와
`frontend/.env`의 `VITE_API_BASE_URL`을 함께 바꾼다.

## Railway 배포

`Dockerfile`(운영용, nginx 정적 서빙)과 `Dockerfile.dev`(로컬 dev server, docker-compose가
사용)를 분리해뒀다 — Railway는 기본 파일명 `Dockerfile`을 찾으므로 별도 설정이 필요 없다.
Vite는 빌드 시점에 환경변수를 번들에 굽기 때문에 `VITE_API_BASE_URL`을 **빌드 전에** 설정해야
한다:

```bash
railway variable set "VITE_API_BASE_URL=<백엔드 공개 URL>" --service golfmate-frontend --skip-deploys
railway up frontend --path-as-root --service golfmate-frontend --ci
railway domain --service golfmate-frontend --port 80
```

## 디렉터리

| 경로 | 역할 |
|---|---|
| `src/pages/` | 라우트 단위 화면 |
| `src/components/` | 여러 페이지에서 재사용하는 UI 조각 (ProtectedRoute 등) |
| `src/context/` | 전역 클라이언트 상태 (로그인한 사용자) |
| `src/api/` | axios 클라이언트, 백엔드 호출 함수 |
| `src/hooks/` | React Query 기반 커스텀 훅 |
| `src/types/` | 백엔드 응답과 대응하는 TypeScript 타입 |

각 폴더의 상세 설명은 폴더 안의 README.md를 참고한다.
