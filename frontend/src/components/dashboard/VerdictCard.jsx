import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";

import Card from "../common/Card.jsx";
import ConfidenceMeter from "./ConfidenceMeter.jsx";
import RiskLevelBadge from "./RiskLevelBadge.jsx";

function getVerdictTone(prediction = "") {
  const value = String(prediction).toLowerCase();
  if (value.includes("fake") || value.includes("manipulated") || value.includes("giả")) {
    return {
      icon: ShieldAlert,
      border: "border-red-400/35",
      bg: "bg-red-400/10",
      text: "text-red-200",
      label: "Có dấu hiệu giả mạo",
      summary: "Nên kiểm tra kỹ các vùng nóng, đoạn video nghi vấn và báo cáo giải thích trước khi kết luận cuối cùng.",
    };
  }
  if (value.includes("real") || value.includes("authentic")) {
    return {
      icon: CheckCircle2,
      border: "border-emerald-400/35",
      bg: "bg-emerald-400/10",
      text: "text-emerald-200",
      label: "Chưa thấy dấu hiệu giả mạo rõ",
      summary: "Kết quả hiện tại nghiêng về nội dung thật, nhưng vẫn nên đối chiếu vùng nghi ngờ và nguồn gốc tệp.",
    };
  }
  return {
    icon: AlertTriangle,
    border: "border-yellow-400/35",
    bg: "bg-yellow-400/10",
    text: "text-yellow-200",
    label: "Cần xem xét thêm",
    summary: "Tín hiệu chưa đủ mạnh để kết luận. Hãy kiểm tra thêm vùng nghi ngờ, chất lượng tệp và thử phân tích lại nếu cần.",
  };
}

function VerdictCard({ result }) {
  const tone = getVerdictTone(result?.prediction);
  const Icon = tone.icon;
  const confidence = Math.round(Number(result?.confidence) || 0);
  const requiresReview = Boolean(result?.requiresReview);
  const decisionMargin = Number(result?.decisionMargin);
  const decisionThreshold = Number(result?.decisionThreshold);

  return (
    <Card className={`overflow-hidden ${tone.border}`}>
      <div className="border-b border-shield-line bg-slate-950/35 p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${tone.bg} ${tone.text}`}>
              <Icon size={26} />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Kết luận sơ bộ</p>
              <h3 className={`mt-1 text-2xl font-bold ${tone.text}`}>{tone.label}</h3>
            </div>
          </div>
          <RiskLevelBadge level={result?.riskLevel} />
        </div>
      </div>

      <div className="grid gap-6 p-5 lg:grid-cols-[1fr_18rem]">
        <div>
          <p className="leading-7 text-slate-300">{tone.summary}</p>
          {requiresReview && (
            <div className="mt-4 flex gap-3 rounded-lg border border-yellow-300/30 bg-yellow-300/10 p-3 text-sm leading-6 text-yellow-100">
              <AlertTriangle className="mt-0.5 shrink-0" size={18} />
              <div>
                <p className="font-semibold">Cần kiểm duyệt thủ công</p>
                <p className="text-yellow-100/80">
                  Xác suất nằm sát ngưỡng quyết định, không nên dùng kết quả này như kết luận tự động.
                </p>
              </div>
            </div>
          )}
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Signal label="Dự đoán gốc" value={result?.prediction || "UNKNOWN"} />
            <Signal label="Độ tin cậy" value={`${confidence}%`} />
            <Signal label="Mã báo cáo" value={result?.reportId || "Chưa tạo"} />
            {Number.isFinite(decisionThreshold) && (
              <Signal label="Ngưỡng quyết định" value={decisionThreshold.toFixed(2)} />
            )}
            {Number.isFinite(decisionMargin) && (
              <Signal label="Biên quyết định" value={decisionMargin.toFixed(2)} />
            )}
          </div>
        </div>
        <div className="rounded-xl border border-shield-line bg-slate-950/45 p-4">
          <ConfidenceMeter value={confidence} />
          <p className="mt-3 text-xs leading-5 text-slate-500">
            Độ tin cậy không phải kết luận pháp lý tuyệt đối. Nó cho biết mô hình đang nghiêng về hướng nào với dữ liệu hiện có.
          </p>
        </div>
      </div>
    </Card>
  );
}

function Signal({ label, value }) {
  return (
    <div className="rounded-lg border border-shield-line bg-slate-950/40 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-slate-100" title={String(value)}>
        {value}
      </p>
    </div>
  );
}

export default VerdictCard;
