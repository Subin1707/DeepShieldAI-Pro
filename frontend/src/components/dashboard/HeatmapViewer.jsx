import { AlertTriangle, Crosshair, Eye, ListChecks, ScanSearch, ZoomIn } from "lucide-react";

import Card from "../common/Card.jsx";
import { API_BASE_URL } from "../../services/api";

const focusAreaLabels = {
  "Eye region": "Vùng mắt",
  "Nose region": "Vùng mũi",
  "Mouth region": "Vùng miệng",
  "Mouth boundary": "Viền miệng",
  "Skin texture": "Kết cấu da",
  "Face edge": "Viền khuôn mặt",
  "Face boundary": "Viền khuôn mặt",
  Lighting: "Ánh sáng",
  "Mouth motion": "Chuyển động miệng",
};

function translateFocusArea(area) {
  return focusAreaLabels[area] || area;
}

function HeatmapViewer({ imageUrl, focusAreas = [], suspiciousRegions = [] }) {
  const resolvedImageUrl = imageUrl?.startsWith("/storage")
    ? `${API_BASE_URL}${imageUrl}`
    : imageUrl;

  const regions = Array.isArray(suspiciousRegions) ? suspiciousRegions : [];
  const indexedRegions = [...regions].sort(
    (a, b) => Number(a.overlayIndex || 999) - Number(b.overlayIndex || 999),
  );
  const strongest = [...regions].sort((a, b) => Number(b.score || 0) - Number(a.score || 0))[0];

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-shield-line bg-slate-950/35 px-5 py-4">
        <div className="flex items-center gap-2">
          <ScanSearch className="text-shield-cyan" size={20} />
          <div>
            <h3 className="font-semibold text-white">Bản đồ vùng nghi ngờ</h3>
            <p className="mt-1 text-xs text-slate-500">
              Ảnh được căn vừa khung để dễ quan sát đối tượng, không phóng quá to và không tạo khoảng trống dư.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <Legend color="bg-red-400" label="Rủi ro cao" />
          <Legend color="bg-yellow-300" label="Cần soi kỹ" />
          <Legend color="bg-cyan-300" label="Tín hiệu nhẹ" />
        </div>
      </div>

      <div className="bg-slate-950/70 px-4 py-5">
        {resolvedImageUrl ? (
          <div className="flex w-full justify-center">
            <div className="flex w-full max-w-[1120px] rounded-lg border border-shield-line bg-black p-3 shadow-[0_18px_45px_rgba(2,6,23,0.35)]">
              <img
                src={resolvedImageUrl}
                alt="Bản đồ vùng nghi ngờ"
                className="mx-auto block h-auto max-h-[min(78vh,820px)] w-full object-contain"
              />
            </div>
          </div>
        ) : (
          <div className="grid min-h-[22rem] w-full place-items-center rounded-lg border border-shield-line bg-[radial-gradient(circle_at_center,rgba(34,211,238,0.14),transparent_45%)] text-slate-500">
            Chưa có ảnh heatmap.
          </div>
        )}
      </div>

      <div className="border-t border-shield-line bg-slate-950/80 px-4 py-3">
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
          <span className="inline-flex items-center gap-2">
            <Crosshair size={14} className="text-cyan-300" />
            Vùng nóng đỏ/vàng là Grad-CAM; số trên ảnh đánh dấu mắt, mũi, miệng hoặc hotspot cần soi.
          </span>
          <span className="inline-flex items-center gap-2">
            <ZoomIn size={14} className="text-cyan-300" />
            Ảnh giữ nguyên tỉ lệ nên không bị cắt vào nội dung phân tích.
          </span>
        </div>
      </div>

      <aside className="border-t border-shield-line bg-shield-panel p-5">
        <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
          <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.04] p-4">
            <div className="flex items-start gap-3">
              <Eye className="mt-0.5 shrink-0 text-cyan-300" size={20} />
              <div>
                <p className="text-sm font-semibold text-white">Điểm nổi bật nhất</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">
                  {strongest
                    ? `${strongest.label}: ${Math.round(Number(strongest.score) || 0)}%, mức ${strongest.severity || "không rõ"}.`
                    : "Chưa có điểm nghi ngờ rõ ràng trong heatmap này."}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-shield-line bg-slate-950/35 p-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Vùng cần chú ý</p>
            <div className="flex flex-wrap gap-2">
              {(focusAreas.length ? focusAreas : ["Face boundary", "Lighting", "Mouth motion"]).map((area) => (
                <span key={area} className="rounded-full border border-cyan-400/30 bg-cyan-400/5 px-3 py-1 text-xs text-cyan-200">
                  {translateFocusArea(area)}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
            <ListChecks size={16} className="text-yellow-300" />
            Giải thích điểm nghi ngờ
          </div>

          {indexedRegions.length > 0 ? (
            <div className="grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
              {indexedRegions.map((region, index) => (
                <RegionCard key={`${region.label}-${index}`} region={region} index={region.overlayIndex || index + 1} />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-shield-line bg-slate-950/45 p-4 text-sm leading-6 text-slate-400">
              Chưa có vùng nghi ngờ để giải thích. Nếu ảnh/video quá mờ, hãy thử tệp rõ hơn hoặc phân tích đoạn khác.
            </div>
          )}
        </div>
      </aside>
    </Card>
  );
}

function RegionCard({ region, index }) {
  const score = Math.round(Number(region.score) || 0);
  const tone = score >= 60 ? "red" : score >= 35 ? "yellow" : "cyan";
  const toneClasses = {
    red: "border-red-400/25 bg-red-400/[0.05]",
    yellow: "border-yellow-400/25 bg-yellow-400/[0.05]",
    cyan: "border-cyan-400/25 bg-cyan-400/[0.05]",
  };
  const barColor = {
    red: "bg-red-400",
    yellow: "bg-yellow-300",
    cyan: "bg-cyan-300",
  };

  return (
    <article className={`rounded-xl border p-4 ${toneClasses[tone]}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-950 text-sm font-bold text-white">
            {index}
          </span>
          <div className="min-w-0">
            <p className="font-semibold text-white">{region.label || "Điểm nghi ngờ"}</p>
            <p className="mt-1 text-xs text-slate-400">Mức độ: {region.severity || "Không rõ"}</p>
          </div>
        </div>
        <span className="rounded-full bg-slate-950 px-2 py-1 text-xs font-bold text-white">{score}%</span>
      </div>

      <div className="mt-3 h-2 rounded-full bg-slate-800">
        <div className={`h-2 rounded-full ${barColor[tone]}`} style={{ width: `${Math.max(4, Math.min(100, score))}%` }} />
      </div>

      {region.reason && (
        <p className="mt-3 text-sm leading-6 text-slate-300">
          <span className="font-semibold text-white">Vì sao nghi ngờ: </span>
          {region.reason}
        </p>
      )}

      {region.manualCheck && (
        <p className="mt-2 text-sm leading-6 text-slate-400">
          <span className="font-semibold text-cyan-200">Cách kiểm tra: </span>
          {region.manualCheck}
        </p>
      )}

      {region.bbox && (
        <p className="mt-3 inline-flex items-center gap-2 rounded-lg border border-shield-line bg-slate-950/45 px-2 py-1 text-xs text-slate-500">
          <AlertTriangle size={13} />
          x {Math.round(region.bbox.x * 100)}%, y {Math.round(region.bbox.y * 100)}%, rộng {Math.round(region.bbox.width * 100)}%, cao {Math.round(region.bbox.height * 100)}%
        </p>
      )}
    </article>
  );
}

function Legend({ color, label }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-shield-line bg-slate-950/45 px-3 py-1 text-slate-400">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      {label}
    </span>
  );
}

export default HeatmapViewer;
