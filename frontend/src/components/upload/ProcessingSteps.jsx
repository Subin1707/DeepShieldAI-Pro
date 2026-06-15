import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const steps = [
  "Kiểm tra định dạng tệp",
  "Lưu tệp vào backend",
  "Tách metadata và frame",
  "Chạy mô hình phân tích",
  "Tạo heatmap và báo cáo",
];

function ProcessingSteps({ progress = 0, loading = false }) {
  const activeIndex = loading ? Math.min(steps.length - 1, Math.floor(progress / 20)) : -1;

  return (
    <ol className="mt-4 space-y-3 text-sm">
      {steps.map((step, index) => {
        const done = progress >= (index + 1) * 20 || (!loading && progress >= 100);
        const active = loading && index === activeIndex;
        const Icon = done ? CheckCircle2 : active ? Loader2 : Circle;

        return (
          <li key={step} className="flex items-center gap-3 text-slate-400">
            <Icon size={18} className={`${done ? "text-emerald-300" : active ? "animate-spin text-cyan-300" : "text-slate-600"}`} />
            <span className={done || active ? "text-slate-200" : ""}>{step}</span>
          </li>
        );
      })}
    </ol>
  );
}

export default ProcessingSteps;
