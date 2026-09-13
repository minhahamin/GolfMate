import { useHealthCheck } from '../hooks/useHealthCheck';

export default function SystemStatus() {
  const { data, isLoading, isError, error } = useHealthCheck();

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-emerald-800/40 bg-emerald-950/40 p-8 shadow-xl">
        <p className="text-sm uppercase tracking-widest text-emerald-400">GolfMate AI</p>
        <h1 className="mt-1 text-2xl font-semibold text-emerald-50">시스템 연결 상태</h1>
        <p className="mt-1 text-sm text-emerald-200/70">
          React → FastAPI → PostgreSQL 연결을 확인합니다.
        </p>

        <div className="mt-6 flex items-center gap-3 rounded-lg bg-black/20 p-4">
          <span
            className={`h-3 w-3 rounded-full ${
              isLoading
                ? 'bg-yellow-400 animate-pulse'
                : isError
                  ? 'bg-red-500'
                  : 'bg-emerald-400'
            }`}
          />
          <span className="text-sm text-emerald-50">
            {isLoading && '연결 확인 중...'}
            {isError && `연결 실패: ${(error as Error).message}`}
            {data && `정상 — status: ${data.status}, database: ${data.database}`}
          </span>
        </div>

        <p className="mt-6 text-xs text-emerald-200/50">
          Phase 1 — 기본 인프라 연결 확인 페이지. 다음 Phase에서 로그인/대시보드로 대체됩니다.
        </p>
      </div>
    </main>
  );
}
