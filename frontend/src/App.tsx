import { Navigate, Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import SystemStatus from './pages/SystemStatus';

function Home() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  return <Navigate to={user ? '/dashboard' : '/login'} replace />;
}

// Phase 2: 인증 라우트(/login, /register)와 보호된 /dashboard가 추가됐다.
// Phase 1의 SystemStatus는 인프라 점검용으로 /status에 남겨둔다.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="/status" element={<SystemStatus />} />
    </Routes>
  );
}
