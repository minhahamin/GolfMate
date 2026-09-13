import { useHealthCheck } from '../hooks/useHealthCheck';

export default function SystemStatus() {
  const { data, isLoading, isError, error } = useHealthCheck();

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper px-4">
      <div className="w-full max-w-md border border-ink/15 p-8">
        <h1 className="font-display text-2xl text-ink">시스템 연결 상태</h1>
        <p className="mt-1 text-sm text-ink-soft">React → FastAPI → PostgreSQL 연결을 확인합니다.</p>

        <div className="mt-6 flex items-center gap-3 border border-ink/15 bg-paper-2 p-4">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              isLoading ? 'bg-sand animate-pulse' : isError ? 'bg-flag' : 'bg-fairway'
            }`}
          />
          <span className="text-sm text-ink">
            {isLoading && '연결 확인 중...'}
            {isError && `연결 실패: ${(error as Error).message}`}
            {data && `정상 — status: ${data.status}, database: ${data.database}`}
          </span>
        </div>

        <p className="mt-6 text-xs text-ink-soft">
          인프라 연결 확인용 페이지입니다.
        </p>
      </div>
    </main>
  );
}
