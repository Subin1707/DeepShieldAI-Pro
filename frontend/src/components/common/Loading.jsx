function Loading({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-400">
      <span className="h-3 w-3 animate-pulse rounded-full bg-cyan-300" />
      {label}
    </div>
  );
}

export default Loading;
