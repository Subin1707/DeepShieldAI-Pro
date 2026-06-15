import { Award, BarChart3, CheckCircle2, Clock3, Cpu, Eye, GitCompareArrows, Info } from "lucide-react";

import Card from "../common/Card.jsx";

function AlgorithmMetricsCard({ result }) {
  const rows = buildAlgorithmRows(result);
  if (!rows.length) return null;

  const best = rows.find((row) => row.best) || rows[0];

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-shield-line bg-slate-950/35 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="text-shield-cyan" />
            <div>
              <h3 className="text-lg font-semibold text-white">Bảng số liệu thuật toán</h3>
              <p className="mt-1 text-xs text-slate-400">Đối chiếu độ tin cậy, thời gian xử lý và vai trò của từng thuật toán.</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-100">
            <Award size={14} />
            Tốt nhất: {best.name}
          </span>
        </div>
      </div>

      <div className="p-5">
        <div className="mb-4 rounded-lg border border-emerald-400/20 bg-emerald-400/[0.05] p-4">
          <div className="flex gap-3">
            <CheckCircle2 className="mt-0.5 text-emerald-300" size={20} />
            <p className="text-sm leading-6 text-emerald-50">
              {best.name} đang là thuật toán đóng góp tốt nhất vì {best.reason}
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-shield-line text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-3 font-semibold">Thuật toán</th>
                <th className="px-3 py-3 font-semibold">Độ chính xác</th>
                <th className="px-3 py-3 font-semibold">Thời gian</th>
                <th className="px-3 py-3 font-semibold">Vai trò</th>
                <th className="px-3 py-3 font-semibold">Đánh giá</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-shield-line">
              {rows.map((row) => (
                <tr key={row.name} className={row.best ? "bg-emerald-400/[0.04]" : ""}>
                  <td className="px-3 py-4">
                    <div className="flex items-center gap-2">
                      <row.icon size={17} className={row.best ? "text-emerald-300" : "text-cyan-300"} />
                      <div>
                        <p className="font-semibold text-white">{row.name}</p>
                        <p className="mt-1 text-xs text-slate-500">{row.status}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <span className="font-semibold text-slate-100">{row.accuracy}</span>
                  </td>
                  <td className="px-3 py-4 text-slate-300">{row.time}</td>
                  <td className="max-w-md px-3 py-4 leading-6 text-slate-400">{row.role}</td>
                  <td className="px-3 py-4">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${row.tone}`}>
                      {row.verdict}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex gap-2 rounded-lg border border-shield-line bg-slate-950/45 p-3 text-xs leading-5 text-slate-400">
          <Info size={15} className="mt-0.5 shrink-0 text-cyan-300" />
          Độ chính xác trong bảng là độ tin cậy ước tính trên lần phân tích hiện tại, không phải accuracy huấn luyện cố định của toàn bộ dataset.
        </div>
      </div>
    </Card>
  );
}

function buildAlgorithmRows(result = {}) {
  const times = result.processingTimes || {};
  const confidence = normalizePercent(result.confidence);
  const temporalStats = result.temporalStats || {};
  const embedding = result.embeddingSimilarity || {};
  const hybrid = result.hybridForensics || {};
  const metadata = hybrid.metadata || {};
  const frequency = hybrid.frequency || {};
  const artifacts = hybrid.artifacts || {};
  const strictThreshold = Number(result.fusion?.strictThreshold) || 45;
  const heatmapMethod = normalizeHeatmapMethod(result.heatmapMethod);
  const mode = result.inferenceMode || "";
  const primaryInferenceMs =
    mode === "video_temporal_model"
      ? firstNumber(times.temporalInferenceMs, times.inferenceMs)
      : mode === "forensic_fallback"
        ? firstNumber(times.fallbackInferenceMs, times.inferenceMs)
        : firstNumber(times.frameInferenceMs, times.inferenceMs);
  const embeddingMs = firstNumber(times.embeddingSimilarityMs, times.inferenceMs);

  const rows = [
    {
      name: mode === "video_temporal_model" ? "Video Temporal Model" : "EfficientNet-B0 + Attention",
      icon: Cpu,
      active: result.modelUsed,
      accuracyValue: confidence,
      accuracy: result.modelUsed ? `${confidence}%` : "N/A",
      timeMs: primaryInferenceMs,
      time: formatDuration(primaryInferenceMs),
      role:
        mode === "video_temporal_model"
          ? "Phân tích chuỗi frame để bắt bất thường theo thời gian trong video."
          : "Trích xuất đặc trưng khuôn mặt và phân loại REAL/FAKE theo từng ảnh hoặc frame.",
      status: result.modelUsed ? "Đang dùng trong kết luận" : "Không có model, dùng fallback",
      verdict: result.modelUsed ? "Chính" : "Dự phòng",
      tone: result.modelUsed ? "bg-cyan-400/10 text-cyan-100" : "bg-slate-700/60 text-slate-300",
    },
    {
      name: heatmapMethod === "grad_cam" ? "Grad-CAM" : "Saliency fallback",
      icon: Eye,
      active: true,
      accuracyValue: heatmapMethod === "grad_cam" ? Math.max(70, confidence - 5) : 55,
      accuracy: heatmapMethod === "grad_cam" ? `${Math.max(70, confidence - 5)}%` : "55%",
      timeMs: times.explainabilityMs,
      time: formatDuration(times.explainabilityMs),
      role:
        heatmapMethod === "grad_cam"
          ? "Sinh heatmap từ gradient lớp FAKE để giải thích vùng mô hình tập trung."
          : "Tạo bản đồ saliency khi model Grad-CAM không khả dụng.",
      status: heatmapMethod === "grad_cam" ? "Giải thích bằng gradient thật" : "Giải thích bằng fallback ảnh",
      verdict: heatmapMethod === "grad_cam" ? "Giải thích tốt" : "Tham khảo",
      tone: heatmapMethod === "grad_cam" ? "bg-emerald-400/10 text-emerald-100" : "bg-yellow-400/10 text-yellow-100",
    },
    {
      name: "Metadata Forensics",
      icon: Info,
      active: Boolean(result.hybridForensics),
      accuracyValue: Number(metadata.score) || 0,
      accuracy: result.hybridForensics ? formatPercent(metadata.score) : "N/A",
      timeMs: firstNumber(times.metadataForensicsMs, times.hybridForensicsMs),
      time: formatDuration(firstNumber(times.metadataForensicsMs, times.hybridForensicsMs)),
      role: "Kiểm tra EXIF, camera model, software, thời gian tạo và dấu vết xuất ảnh AI.",
      status: metadata.score >= strictThreshold ? "Có dấu hiệu metadata đáng nghi" : "Metadata không quá bất thường",
      verdict: metadata.score >= strictThreshold ? "Tăng rủi ro" : "Hỗ trợ",
      tone: metadata.score >= strictThreshold ? "bg-red-400/10 text-red-100" : "bg-slate-700/60 text-slate-300",
    },
    {
      name: "FFT Frequency Analysis",
      icon: BarChart3,
      active: Boolean(result.hybridForensics),
      accuracyValue: Number(frequency.score) || 0,
      accuracy: result.hybridForensics ? formatPercent(frequency.score) : "N/A",
      timeMs: firstNumber(times.frequencyAnalysisMs, times.hybridForensicsMs),
      time: formatDuration(firstNumber(times.frequencyAnalysisMs, times.hybridForensicsMs)),
      role: "Dùng Fast Fourier Transform để tìm dấu vết bất thường trong miền tần số.",
      status: frequency.score >= strictThreshold ? "Có bất thường miền tần số" : "Phổ tần số chưa nổi bật",
      verdict: frequency.score >= strictThreshold ? "Forensic mạnh" : "Hỗ trợ",
      tone: frequency.score >= strictThreshold ? "bg-orange-400/10 text-orange-100" : "bg-slate-700/60 text-slate-300",
    },
    {
      name: "AI Artifact Detection",
      icon: Eye,
      active: Boolean(result.hybridForensics),
      accuracyValue: Number(artifacts.score) || 0,
      accuracy: result.hybridForensics ? formatPercent(artifacts.score) : "N/A",
      timeMs: firstNumber(times.artifactDetectionMs, times.hybridForensicsMs),
      time: formatDuration(firstNumber(times.artifactDetectionMs, times.hybridForensicsMs)),
      role: "Đánh giá da quá mịn, residual noise, edge pattern, màu sắc và texture nhân tạo.",
      status: artifacts.score >= strictThreshold ? "Có dấu hiệu ảnh AI render" : "Artifact chưa vượt ngưỡng",
      verdict: artifacts.score >= strictThreshold ? "Siết chặt" : "Hỗ trợ",
      tone: artifacts.score >= strictThreshold ? "bg-purple-400/10 text-purple-100" : "bg-slate-700/60 text-slate-300",
    },
    {
      name: "Face Embedding + Cosine",
      icon: GitCompareArrows,
      active: Boolean(embedding.available),
      accuracyValue: embedding.available ? Math.round((Number(embedding.meanSimilarity) || 0) * 100) : 0,
      accuracy: embedding.available ? formatPercent(embedding.meanSimilarity) : "N/A",
      timeMs: embeddingMs,
      time: embedding.available ? formatDuration(embeddingMs) : "Không áp dụng",
      role: "Đối chiếu độ ổn định khuôn mặt giữa các frame liên tiếp trong video.",
      status: embedding.available ? "Có dữ liệu video liên tiếp" : "Chỉ áp dụng tốt cho video",
      verdict: embedding.available ? "Đối chiếu tốt" : "Không áp dụng",
      tone: embedding.available ? "bg-purple-400/10 text-purple-100" : "bg-slate-700/60 text-slate-300",
    },
    {
      name: "Risk Scoring",
      icon: Clock3,
      active: true,
      accuracyValue: Math.max(40, 100 - Math.abs(50 - confidence)),
      accuracy: `${Math.max(40, 100 - Math.abs(50 - confidence))}%`,
      timeMs: times.riskScoringMs,
      time: formatDuration(times.riskScoringMs, "Tức thì"),
      role: "Tổng hợp xác suất, confidence, frame nghi ngờ và tín hiệu hỗ trợ thành mức rủi ro.",
      status: "Luôn chạy sau phân tích",
      verdict: "Tổng hợp",
      tone: "bg-blue-400/10 text-blue-100",
    },
  ];

  const scoredRows = rows.map((row) => ({
    ...row,
    score: (row.active ? 30 : 0) + row.accuracyValue - Math.min(Number(row.timeMs || 0) / 1000, 20),
  }));
  const best = scoredRows.reduce((current, row) => (row.score > current.score ? row : current), scoredRows[0]);

  return scoredRows.map((row) => ({
    ...row,
    best: row.name === best.name,
    reason: buildBestReason(row, result),
  }));
}

function normalizeHeatmapMethod(method = "") {
  return String(method).toLowerCase().replace(/[-\s]/g, "_") || "saliency_fallback";
}

function buildBestReason(row, result) {
  if (row.name.includes("Temporal")) {
    return "nó trực tiếp dùng chuỗi frame video để đưa ra kết luận chính.";
  }
  if (row.name.includes("EfficientNet")) {
    return "nó tạo xác suất REAL/FAKE chính với confidence cao nhất trong lần chạy này.";
  }
  if (row.name.includes("Grad-CAM")) {
    return "nó giải thích trực quan vùng ảnh ảnh hưởng mạnh nhất đến quyết định FAKE.";
  }
  if (row.name.includes("Metadata")) {
    return "nó phát hiện dấu vết EXIF, software hoặc camera metadata bất thường của ảnh xuất/ảnh AI.";
  }
  if (row.name.includes("FFT")) {
    return "nó tìm được dấu vết bất thường trong miền tần số mà mắt thường khó thấy.";
  }
  if (row.name.includes("Artifact")) {
    return "nó đánh giá trực tiếp texture quá mịn, residual noise thấp và edge pattern bất thường.";
  }
  if (row.name.includes("Embedding")) {
    return "nó phát hiện độ ổn định khuôn mặt giữa các frame và hỗ trợ đối chiếu video.";
  }
  return `nó tổng hợp kết quả thành mức rủi ro ${result.riskLevel || "hiện tại"}.`;
}

function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "0%";
  const number = Number(value);
  return `${Math.round(number <= 1 ? number * 100 : number)}%`;
}

function normalizePercent(value) {
  const number = Number(value) || 0;
  return Math.max(0, Math.min(100, Math.round(number)));
}

function firstNumber(...values) {
  return values.find((value) => Number.isFinite(Number(value)) && Number(value) > 0);
}

function formatDuration(value, fallback = "Chưa có") {
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) return fallback;
  if (number < 1000) return `${Math.round(number)} ms`;
  return `${(number / 1000).toFixed(number >= 10000 ? 1 : 2)} s`;
}

export default AlgorithmMetricsCard;
