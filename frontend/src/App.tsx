import type { ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import Coach from './pages/Coach';
import CourseDetail from './pages/CourseDetail';
import Courses from './pages/Courses';
import Dashboard from './pages/Dashboard';
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
// Phase 1의 SystemStatus는 인프라 점검용으로 /status에 남겨둔다.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={protect(<Dashboard />)} />
      <Route path="/coach" element={protect(<Coach />)} />
      <Route path="/profile" element={protect(<Profile />)} />
      <Route path="/rounds" element={protect(<Rounds />)} />
      <Route path="/rounds/new" element={protect(<RoundNew />)} />
      <Route path="/rounds/:id" element={protect(<RoundDetail />)} />
      <Route path="/courses" element={protect(<Courses />)} />
      <Route path="/courses/:id" element={protect(<CourseDetail />)} />
      <Route path="/status" element={<SystemStatus />} />
    </Routes>
  );
}
