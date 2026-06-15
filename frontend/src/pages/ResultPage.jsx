import {
  Activity,
  AlertTriangle,
  Brain,
  CalendarClock,
  FileText,
  Gauge,
  ImageUp,
  Radar,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import AdvancedAnalysisCard from "../components/dashboard/AdvancedAnalysisCard.jsx";
import AlgorithmMetricsCard from "../components/dashboard/AlgorithmMetricsCard.jsx";
import AIReportCard from "../components/dashboard/AIReportCard.jsx";
import HeatmapViewer from "../components/dashboard/HeatmapViewer.jsx";
import MetricsGrid from "../components/dashboard/MetricsGrid.jsx";
import RiskScoreGauge from "../components/dashboard/RiskScoreGauge.jsx";
import TrainingLossChart from "../components/dashboard/TrainingLossChart.jsx";
import VerdictCard from "../components/dashboard/VerdictCard.jsx";
import Card from "../components/common/Card.jsx";
import EmptyState from "../components/common/EmptyState.jsx";

function ResultPage() {
  const result = getLatestResult();

  if (!result) {
    return (
      <EmptyState
        title="Chưa có kết quả phân tích"
        text="Hãy tải ảnh hoặc video nghi vấn lên trước, hệ thống sẽ tạo bảng kết quả kèm bản đồ vùng nghi ngờ."
        actionLabel="Tải tệp lên"
        icon={ImageUp}
      />
    );
  }

  const confidence = normalizePercent(result.confidence);
  const riskScore = Number(result.riskScore) || 0;
  const temporalStats = result.temporalStats || {};
  const suspiciousFrameRatio = temporalStats.suspiciousFrameRatio ?? 0;
  const regions = Array.isArray(result.suspiciousRegions) ? result.suspiciousRegions : [];

  const metrics = [
    {
      label: "Kết luận",
      value: toVietnamesePrediction(result.prediction),
      hint: "Dựa trên mô hình học sâu và dấu hiệu pháp chứng ảnh.",
      icon: ShieldCheck,
      tone: isFake(result.prediction) ? "danger" : "safe",
    },
    {
      label: "Độ tin cậy",
      value: `${confidence}%`,
      hint: "Mức chắc chắn của kết luận hiện tại.",
      icon: Gauge,
      tone: confidence >= 70 ? "info" : "warning",
    },
    {
      label: "Mức rủi ro",
      value: toVietnameseRisk(result.riskLevel),
      hint: "Ước lượng rủi ro tổng hợp từ điểm và vùng nóng.",
      icon: AlertTriangle,
      tone: riskScore >= 70 ? "danger" : riskScore >= 40 ? "warning" : "safe",
    },
    {
      label: "Vùng nghi ngờ",
      value: regions.length,
      hint: "Các điểm nổi bật cần kiểm tra thủ công.",
      icon: Radar,
      tone: regions.length > 0 ? "warning" : "safe",
    },
  ];

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-cyan-400/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.14),transparent_34%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(2,6,23,0.98))]">
        <div className="grid gap-6 p-6 lg:grid-cols-[1.4fr_0.8fr] lg:p-8">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              <Sparkles size={14} />
              Bảng kết quả điều tra Deepfake
            </div>
            <h1 className="text-3xl font-bold text-white md:text-4xl">Kết quả phân tích</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300 md:text-base">
              Hệ thống tổng hợp kết luận, độ tin cậy, mức rủi ro, bản đồ vùng nghi ngờ và báo cáo giải thích để bạn kiểm tra video/ảnh theo từng dấu hiệu cụ thể.
            </p>

            <div className="mt-5 flex flex-wrap gap-3 text-xs text-slate-300">
              <InfoPill icon={Activity} label="Chế độ" value={toVietnameseMode(result.inferenceMode)} />
              <InfoPill icon={CalendarClock} label="Thời điểm" value={formatDate(result.createdAt)} />
              <InfoPill icon={Brain} label="Báo cáo" value={result.reportId || "Chưa tạo mã"} />
            </div>
          </div>

          <div className="rounded-xl border border-shield-line bg-slate-950/45 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Tổng quan nhanh</p>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <QuickStat label="Điểm rủi ro" value={riskScore} suffix="/100" />
              <QuickStat label="Frame nghi ngờ" value={suspiciousFrameRatio} suffix="%" />
              <QuickStat label="Độ tin cậy" value={confidence} suffix="%" />
              <QuickStat label="Đoạn nghi vấn" value={result.suspiciousSegments?.length || 0} suffix="" />
            </div>
          </div>
        </div>
      </section>

      <MetricsGrid metrics={metrics} />

      <section className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_24rem]">
        <div className="space-y-6">
          <VerdictCard result={result} />
          <AlgorithmMetricsCard result={result} />
          <TrainingLossChart result={result} />
          <HeatmapViewer
            imageUrl={result.heatmapUrl}
            focusAreas={result.focusAreas}
            suspiciousRegions={result.suspiciousRegions}
          />
          <AdvancedAnalysisCard
            temporalStats={result.temporalStats}
            suspiciousSegments={result.suspiciousSegments}
            inferenceMode={result.inferenceMode}
            embeddingSimilarity={result.embeddingSimilarity}
          />
          <AIReportCard report={result.aiReport} reportId={result.reportId} />
        </div>

        <aside className="space-y-4 2xl:sticky 2xl:top-24 2xl:self-start">
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <Activity className="text-shield-cyan" />
              <h3 className="font-semibold text-white">Điểm rủi ro tổng hợp</h3>
            </div>
            <RiskScoreGauge value={riskScore} />
            <p className="mt-4 text-sm leading-6 text-slate-400">
              Điểm càng cao thì khả năng có thao tác chỉnh sửa, ghép mặt hoặc bất thường theo thời gian càng đáng chú ý.
            </p>
          </Card>

          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <FileText className="text-shield-cyan" />
              <h3 className="font-semibold text-white">Hồ sơ báo cáo</h3>
            </div>
            <div className="space-y-3 text-sm text-slate-400">
              <p>Mã báo cáo: <span className="font-semibold text-slate-200">{result.reportId || "Chưa tạo"}</span></p>
              <p>Kết luận: <span className="font-semibold text-slate-200">{toVietnamesePrediction(result.prediction)}</span></p>
              <p>Vùng cần chú ý: <span className="font-semibold text-slate-200">{regions.length}</span></p>
            </div>
            {result.reportId && (
              <a className="mt-5 inline-flex rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-400/20" href="#/reports">
                Xem báo cáo đầy đủ
              </a>
            )}
          </Card>
        </aside>
      </section>
    </div>
  );
}

function InfoPill({ icon: Icon, label, value }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-shield-line bg-slate-950/50 px-3 py-2">
      <Icon size={14} className="text-cyan-300" />
      <span className="text-slate-500">{label}:</span>
      <span className="font-semibold text-slate-200">{value}</span>
    </span>
  );
}

function QuickStat({ label, value, suffix }) {
  return (
    <div className="rounded-lg border border-shield-line bg-slate-950/60 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-white">
        {value}
        <span className="text-sm text-slate-500">{suffix}</span>
      </p>
    </div>
  );
}

function getLatestResult() {
  try {
    const raw = localStorage.getItem("latestAnalysisResult");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function normalizePercent(value) {
  const number = Number(value) || 0;
  return Math.max(0, Math.min(100, Math.round(number)));
}

function isFake(prediction = "") {
  const value = String(prediction).toLowerCase();
  return value.includes("fake") || value.includes("manipulated") || value.includes("giả");
}

function toVietnamesePrediction(prediction = "") {
  const value = String(prediction).toLowerCase();
  if (value.includes("fake") || value.includes("manipulated")) return "Có dấu hiệu giả mạo";
  if (value.includes("real") || value.includes("authentic")) return "Chưa thấy giả mạo rõ";
  return "Cần xem xét thêm";
}

function toVietnameseRisk(level = "") {
  const value = String(level).toLowerCase();
  if (value.includes("high")) return "Cao";
  if (value.includes("medium")) return "Trung bình";
  if (value.includes("low")) return "Thấp";
  return level || "Chưa rõ";
}

function toVietnameseMode(mode = "") {
  const labels = {
    video_temporal_model: "Mô hình video theo chuỗi thời gian",
    deep_learning_model: "Mô hình học sâu theo từng frame",
    forensic_fallback: "Phân tích fallback bằng dấu hiệu ảnh",
  };
  return labels[mode] || mode || "Chưa xác định";
}

function formatDate(value) {
  if (!value) return "Vừa phân tích";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Vừa phân tích";
  return date.toLocaleString("vi-VN");
}

export default ResultPage;
