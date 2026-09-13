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
      <div className="flex justify-between text-sm text-ink-soft">
        <span>{label}</span>
        <span className="font-mono text-ink">{displayValue ?? `${clamped.toFixed(0)}%`}</span>
      </div>
      <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-paper-2">
        <div
          className="h-full rounded-full bg-fairway transition-all"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
