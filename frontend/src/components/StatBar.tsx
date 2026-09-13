// §22의 "████████░░" 스타일 비율 시각화. GIR/페어웨이/퍼팅 등 0~100 지표에 쓴다.
export default function StatBar({
  label,
  value,
  displayValue,
}: {
  label: string;
  value: number;
  displayValue?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div>
      <div className="flex justify-between text-sm text-emerald-200/70">
        <span>{label}</span>
        <span className="text-emerald-100">{displayValue ?? `${clamped.toFixed(0)}%`}</span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-emerald-900/40">
        <div
          className="h-full rounded-full bg-emerald-400 transition-all"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
