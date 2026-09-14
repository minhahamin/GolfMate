import type { ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import BetDetail from './pages/BetDetail';
import BetNew from './pages/BetNew';
import Caddie from './pages/Caddie';
import Coach from './pages/Coach';
import CourseDetail from './pages/CourseDetail';
import CourseRecommend from './pages/CourseRecommend';
import Courses from './pages/Courses';
import Dashboard from './pages/Dashboard';
import Diary from './pages/Diary';
import DiaryDetail from './pages/DiaryDetail';
import DiaryNew from './pages/DiaryNew';
import GroupDetail from './pages/GroupDetail';
import Groups from './pages/Groups';
import Login from './pages/Login';
import Profile from './pages/Profile';
import Register from './pages/Register';
import RoundDetail from './pages/RoundDetail';
import RoundNew from './pages/RoundNew';
import Rounds from './pages/Rounds';
import SystemStatus from './pages/SystemStatus';

function Home() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  return <Navigate to={user ? '/dashboard' : '/login'} replace />;
}

function protect(element: ReactNode) {
  return <ProtectedRoute>{element}</ProtectedRoute>;
}

// Phase 3: 골프 데이터 라우트(/courses, /rounds, /profile)가 추가됐다.
// Phase 4: /coach(AI Coach)가 추가됐다.
// Phase 6: /diary(AI 골프 일기)가 추가됐다.
// Phase 7: /courses/recommend(AI 골프장 추천)가 추가됐다 — /courses/:id보다 먼저 등록해야
// "recommend"가 id로 오인되지 않는다.
// Phase 8: /caddie(AI 캐디)가 추가됐다.
// Phase 9: /groups(내기 모임), /bets/:id(내기 상세 + AI 코멘터리)가 추가됐다.
// Phase 1의 SystemStatus는 인프라 점검용으로 /status에 남겨둔다.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={protect(<Dashboard />)} />
      <Route path="/coach" element={protect(<Coach />)} />
      <Route path="/caddie" element={protect(<Caddie />)} />
      <Route path="/profile" element={protect(<Profile />)} />
      <Route path="/rounds" element={protect(<Rounds />)} />
      <Route path="/rounds/new" element={protect(<RoundNew />)} />
      <Route path="/rounds/:id" element={protect(<RoundDetail />)} />
      <Route path="/courses" element={protect(<Courses />)} />
      <Route path="/courses/recommend" element={protect(<CourseRecommend />)} />
      <Route path="/courses/:id" element={protect(<CourseDetail />)} />
      <Route path="/diary" element={protect(<Diary />)} />
      <Route path="/diary/new" element={protect(<DiaryNew />)} />
      <Route path="/diary/:id" element={protect(<DiaryDetail />)} />
      <Route path="/groups" element={protect(<Groups />)} />
      <Route path="/groups/:id" element={protect(<GroupDetail />)} />
      <Route path="/groups/:id/bets/new" element={protect(<BetNew />)} />
      <Route path="/bets/:id" element={protect(<BetDetail />)} />
      <Route path="/status" element={<SystemStatus />} />
    </Routes>
  );
}
