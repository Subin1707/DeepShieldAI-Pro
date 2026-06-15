function RiskScoreGauge({ value = 0 }) {
  const score = Math.max(0, Math.min(100, Number(value) || 0));
  const color = score >= 70 ? "#f87171" : score >= 40 ? "#facc15" : "#34d399";
  const label = score >= 70 ? "Cao" : score >= 40 ? "Trung bình" : "Thấp";

  return (
    <div className="relative mx-auto grid h-40 w-40 place-items-center rounded-full bg-slate-900">
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(${color} ${score * 3.6}deg, #1e293b 0deg)`,
        }}
      />
      <div className="relative grid h-32 w-32 place-items-center rounded-full border border-shield-line bg-shield-panel">
        <div className="text-center">
          <p className="text-4xl font-bold text-white">{score}</p>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">rủi ro</p>
          <p className="mt-1 text-sm font-semibold" style={{ color }}>
            {label}
          </p>
        </div>
      </div>
    </div>
  );
}

export default RiskScoreGauge;
