import { BarChart3, Clock3, Eye, GitCompareArrows, Layers3, ScanSearch } from "lucide-react";

import Card from "../common/Card.jsx";

function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) return "0%";
  const number = Number(value);
  return `${Math.round(number <= 1 ? number * 100 : number)}%`;
}

function AdvancedAnalysisCard({ temporalStats, suspiciousSegments = [], inferenceMode, embeddingSimilarity }) {
  if (!temporalStats && suspiciousSegments.length === 0 && !inferenceMode && !embeddingSimilarity) return null;

  const modeLabels = {
    video_temporal_model: "Mô hình video theo chuỗi thời gian",
    deep_learning_model: "Mô hình học sâu theo từng frame",
    forensic_fallback: "Phân tích fallback bằng dấu hiệu ảnh",
  };

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-shield-line bg-slate-950/35 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="text-shield-cyan" />
            <h3 className="text-lg font-semibold text-white">Phân tích nâng cao</h3>
          </div>
          {inferenceMode && (
            <span className="rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              {modeLabels[inferenceMode] || inferenceMode}
            </span>
          )}
        </div>
      </div>

      <div className="space-y-5 p-5">
        <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.04] p-4">
          <div className="flex gap-3">
            <ScanSearch className="mt-0.5 text-cyan-300" size={20} />
            <p className="text-sm leading-6 text-cyan-50">
              Phần này đọc các tín hiệu theo thời gian: mức nghi giả trung bình, đỉnh bất thường, độ dao động giữa các frame và các đoạn video cần soi lại.
            </p>
          </div>
        </div>

        {temporalStats && (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Stat icon={Eye} label="Trung bình nghi giả" value={formatPercent(temporalStats.meanFakeProbability)} />
            <Stat icon={Layers3} label="Đỉnh bất thường" value={formatPercent(temporalStats.maxFakeProbability)} />
            <Stat icon={BarChart3} label="Độ dao động" value={formatPercent(temporalStats.temporalVariance)} />
            <Stat icon={Clock3} label="Frame nghi ngờ" value={`${temporalStats.suspiciousFrameRatio || 0}%`} />
          </div>
        )}

        {embeddingSimilarity?.available && (
          <div>
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
              <GitCompareArrows size={16} className="text-emerald-300" />
              Face embedding similarity
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Stat icon={GitCompareArrows} label="Mean similarity" value={formatPercent(embeddingSimilarity.meanSimilarity)} />
              <Stat icon={Eye} label="Lowest similarity" value={formatPercent(embeddingSimilarity.minSimilarity)} />
              <Stat icon={Layers3} label="Max similarity drop" value={formatPercent(embeddingSimilarity.maxSimilarityDrop)} />
              <Stat icon={Clock3} label="Suspicious transitions" value={`${embeddingSimilarity.suspiciousTransitionRatio || 0}%`} />
            </div>
          </div>
        )}

        {suspiciousSegments.length > 0 ? (
          <div>
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
              <Clock3 size={16} className="text-yellow-300" />
              Các đoạn video nghi ngờ nhất
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {suspiciousSegments.map((segment, index) => (
                <div key={`${segment.startFrame}-${segment.endFrame}-${index}`} className="rounded-xl border border-yellow-400/25 bg-yellow-400/[0.05] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">
                        Đoạn {index + 1}: frame {segment.startFrame} đến {segment.endFrame}
                      </p>
                      <p className="mt-2 text-xs leading-5 text-slate-400">
                        Nên tua lại đoạn này để kiểm tra mép mặt, miệng, mắt, ánh sáng và độ khớp chuyển động.
                      </p>
                    </div>
                    <span className="rounded-full bg-yellow-300 px-2 py-1 text-xs font-bold text-slate-950">
                      {formatPercent(segment.maxFakeProbability)}
                    </span>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-slate-800">
                    <div
                      className="h-2 rounded-full bg-yellow-300"
                      style={{ width: formatPercent(segment.meanFakeProbability) }}
                    />
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    Trung bình {formatPercent(segment.meanFakeProbability)}, cao nhất {formatPercent(segment.maxFakeProbability)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="rounded-xl border border-shield-line bg-slate-950/45 p-4 text-sm text-slate-400">
            Chưa phát hiện đoạn video nổi bật theo thời gian. Nếu video quá ngắn hoặc chất lượng thấp, hãy thử tệp có độ phân giải tốt hơn.
          </p>
        )}
      </div>
    </Card>
  );
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl border border-shield-line bg-slate-950/50 p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <p className="text-xs text-slate-500">{label}</p>
        <Icon size={16} className="text-cyan-300" />
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

export default AdvancedAnalysisCard;
