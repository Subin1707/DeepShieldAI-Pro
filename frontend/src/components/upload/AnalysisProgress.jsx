function AnalysisProgress({ progress = 0, loading = false, label = "Đang tải lên và phân tích" }) {
  const value = Math.max(0, Math.min(100, progress));

  if (!loading && value === 0) return null;

  return (
    <div className="mt-6 rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-4">
      <div className="mb-2 flex justify-between text-sm text-slate-300">
        <span>{label}</span>
        <span className="font-semibold text-cyan-200">{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-cyan-400 transition-all duration-300" style={{ width: `${value}%` }} />
      </div>
      <p className="mt-3 text-xs leading-5 text-slate-500">
        Hệ thống đang chuẩn bị frame, metadata, tín hiệu mô hình, heatmap và báo cáo giải thích.
      </p>
    </div>
  );
}

export default AnalysisProgress;
