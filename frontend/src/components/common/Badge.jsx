function Badge({ children, tone = "neutral", className = "" }) {
  const tones = {
    neutral: "border-slate-600 bg-slate-900/70 text-slate-200",
    info: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
    success: "border-green-400/30 bg-green-400/10 text-green-200",
    warning: "border-yellow-400/30 bg-yellow-400/10 text-yellow-200",
    danger: "border-red-400/30 bg-red-400/10 text-red-200",
  };

  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${tones[tone]} ${className}`}>
      {children}
    </span>
  );
}

export default Badge;
