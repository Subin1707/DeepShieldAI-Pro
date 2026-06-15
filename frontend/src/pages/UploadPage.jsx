import { useMemo, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  FileVideo,
  Info,
  Radar,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";

import AnalysisProgress from "../components/upload/AnalysisProgress.jsx";
import FilePreview from "../components/upload/FilePreview.jsx";
import ProcessingSteps from "../components/upload/ProcessingSteps.jsx";
import UploadBox from "../components/upload/UploadBox.jsx";
import { analyzeFile } from "../services/analysisService";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const fileKind = useMemo(() => {
    if (!file) return "Chưa chọn tệp";
    if (file.type?.startsWith("video/")) return "Video";
    if (file.type?.startsWith("image/")) return "Ảnh";
    return "Tệp khác";
  }, [file]);

  const handleAnalyze = async () => {
    setError("");
    setResult(null);

    if (!file) {
      setError("Bạn cần chọn ảnh hoặc video trước khi phân tích.");
      return;
    }

    setLoading(true);
    setProgress(0);

    try {
      const data = await analyzeFile(file, (event) => {
        if (!event.total) return;
        setProgress(Math.round((event.loaded * 100) / event.total));
      });

      setResult(data);
      localStorage.setItem("latestAnalysisResult", JSON.stringify(data));
      window.location.hash = "#/results";
    } catch (err) {
      setError(err.message || "Không thể phân tích tệp này.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-cyan-400/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.14),transparent_32%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(2,6,23,0.98))] p-6 lg:p-8">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              <Sparkles size={14} />
              Deepfake evidence intake
            </div>
            <h1 className="text-3xl font-bold text-white">Tải bằng chứng cần kiểm tra</h1>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
              Chọn ảnh hoặc video nghi vấn. Hệ thống sẽ lưu tệp, trích xuất frame, chạy mô hình, sinh heatmap và tạo báo cáo giải thích bằng tiếng Việt.
            </p>
          </div>

          <div className="rounded-xl border border-emerald-400/25 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
            <div className="flex items-center gap-2 font-semibold">
              <ShieldCheck size={16} />
              Sẵn sàng phân tích
            </div>
            <p className="mt-1 text-xs text-emerald-100/80">Backend, model và lưu trữ đã kết nối</p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <section className="rounded-xl border border-shield-line bg-shield-panel p-6 lg:p-8">
          <div className="mb-6 grid gap-3 sm:grid-cols-3">
            <IntakeStat label="Loại tệp" value={fileKind} />
            <IntakeStat label="Trạng thái" value={loading ? "Đang xử lý" : file ? "Đã sẵn sàng" : "Chờ tệp"} />
            <IntakeStat label="Đầu ra" value="Heatmap + báo cáo" />
          </div>

          <UploadBox file={file} disabled={loading} onFileSelect={setFile} />
          <FilePreview file={file} onClear={() => setFile(null)} />
          <AnalysisProgress progress={progress} loading={loading} />

          {error && (
            <div className="mt-6 flex items-start gap-2 rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-red-200">
              <AlertCircle className="mt-0.5 shrink-0" size={18} />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="mt-6 flex items-start gap-2 rounded-xl border border-emerald-400/30 bg-emerald-400/10 p-4 text-emerald-200">
              <CheckCircle2 className="mt-0.5 shrink-0" size={18} />
              <span>Phân tích hoàn tất. Đang chuyển sang trang kết quả.</span>
            </div>
          )}

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-5 py-3.5 font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Radar size={18} />
            {loading ? "Đang phân tích..." : "Bắt đầu phân tích AI"}
          </button>
        </section>

        <aside className="space-y-4">
          <div className="rounded-xl border border-shield-line bg-shield-panel p-6">
            <div className="mb-2 flex items-center gap-2">
              <Zap className="text-shield-cyan" size={18} />
              <h3 className="font-semibold text-white">Các bước xử lý</h3>
            </div>
            <ProcessingSteps progress={progress} loading={loading} />
          </div>

          <div className="rounded-xl border border-shield-line bg-shield-panel p-6">
            <div className="mb-4 flex items-center gap-2">
              <Info className="text-shield-cyan" size={18} />
              <h3 className="font-semibold text-white">Hệ thống sẽ kiểm tra</h3>
            </div>
            <ul className="space-y-3 text-sm leading-6 text-slate-400">
              <ChecklistItem>Độ nhất quán giữa các frame trong video.</ChecklistItem>
              <ChecklistItem>Vùng mắt, miệng, mũi và viền khuôn mặt.</ChecklistItem>
              <ChecklistItem>Các điểm saliency cao hoặc texture bất thường.</ChecklistItem>
              <ChecklistItem>Báo cáo giải thích bằng tiếng Việt có dấu.</ChecklistItem>
            </ul>
          </div>

          <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.04] p-6">
            <div className="mb-3 flex items-center gap-2">
              <FileVideo className="text-cyan-300" size={18} />
              <h3 className="font-semibold text-white">Gợi ý file tốt</h3>
            </div>
            <p className="text-sm leading-6 text-slate-400">
              Nên dùng video có khuôn mặt rõ, ít rung, đủ sáng và không bị nén quá mạnh. Với video dài, hãy chọn đoạn có mặt xuất hiện ổn định để kết quả heatmap rõ hơn.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

function IntakeStat({ label, value }) {
  return (
    <div className="rounded-xl border border-shield-line bg-slate-950/45 p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-white">{value}</p>
    </div>
  );
}

function ChecklistItem({ children }) {
  return (
    <li className="flex gap-2">
      <CheckCircle2 className="mt-0.5 shrink-0 text-cyan-300" size={16} />
      <span>{children}</span>
    </li>
  );
}

export default UploadPage;
