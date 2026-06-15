function FrameTimeline({ frames = [] }) {
  const items = frames.length ? frames : [12, 24, 36, 48, 60, 72].map((frame, index) => ({
    frame,
    score: [28, 42, 64, 83, 77, 51][index],
  }));

  return (
    <div className="flex items-end gap-2">
      {items.map((item) => (
        <div key={item.frame} className="flex flex-1 flex-col items-center gap-2">
          <div className="w-full rounded-t bg-cyan-400/70" style={{ height: `${Math.max(16, item.score)}px` }} />
          <span className="text-[10px] text-slate-500">{item.frame}</span>
        </div>
      ))}
    </div>
  );
}

export default FrameTimeline;
