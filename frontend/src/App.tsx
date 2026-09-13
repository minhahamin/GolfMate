import { Route, Routes } from 'react-router-dom';

import SystemStatus from './pages/SystemStatus';

// Phase 1: 라우트는 시스템 상태 확인 페이지 하나뿐이다.
// Phase 2부터 /login, /register, /dashboard 등이 이 자리에 추가된다.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<SystemStatus />} />
    </Routes>
  );
}
