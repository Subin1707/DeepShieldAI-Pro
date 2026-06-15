function ConfidenceMeter({ value = 0, label = "Confidence" }) {
  const confidence = Math.max(0, Math.min(100, Number(value) || 0));
  const color = confidence >= 80 ? "bg-red-400" : confidence >= 55 ? "bg-yellow-300" : "bg-green-400";

  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span className="font-semibold text-white">{confidence}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-800">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${confidence}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>Low</span>
        <span>Model certainty</span>
        <span>High</span>
      </div>
    </div>
  );
}

export default ConfidenceMeter;
