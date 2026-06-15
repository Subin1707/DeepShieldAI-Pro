import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  Clock,
  FileVideo,
  RefreshCw,
  Search,
  ShieldAlert,
  SlidersHorizontal,
} from "lucide-react";

import Card from "../components/common/Card.jsx";
import { getHistory } from "../services/historyService";

const filters = [
  { id: "all", label: "Tất cả" },
  { id: "fake", label: "Nghi giả" },
  { id: "real", label: "Có vẻ thật" },
];

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");

  const loadHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getHistory(1, 50);
      setHistory(data.items || []);
    } catch (err) {
      setError(err.message || "Không tải được lịch sử phân tích.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const stats = useMemo(() => {
    const total = history.length;
    const fake = history.filter((item) => isFake(item.prediction)).length;
    const real = history.filter((item) => isReal(item.prediction)).length;
    const avgConfidence = total
      ? Math.round(history.reduce((sum, item) => sum + (Number(item.confidence) || 0), 0) / total)
      : 0;

    return { total, fake, real, avgConfidence };
  }, [history]);

  const filteredHistory = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    return history.filter((item) => {
      const matchesQuery = !keyword || `${item.fileName || ""} ${item.analysisId || ""}`.toLowerCase().includes(keyword);
      const matchesFilter =
        activeFilter === "all" ||
        (activeFilter === "fake" && isFake(item.prediction)) ||
        (activeFilter === "real" && isReal(item.prediction));

      return matchesQuery && matchesFilter;
    });
  }, [history, query, activeFilter]);

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-cyan-400/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.13),transparent_32%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(2,6,23,0.98))] p-6">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              <Clock size={14} />
              Nhật ký phân tích
            </div>
            <h1 className="text-3xl font-bold text-white">Lịch sử</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
              Theo dõi các lần phân tích đã lưu trong backend, lọc nhanh nội dung nghi giả và mở lại kết quả để xem heatmap hoặc báo cáo.
            </p>
          </div>

          <button
            type="button"
            onClick={loadHistory}
            className="inline-flex items-center gap-2 rounded-lg border border-cyan-400/25 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            Làm mới
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={CalendarClock} label="Tổng phân tích" value={stats.total} tone="cyan" />
        <StatCard icon={ShieldAlert} label="Nghi giả" value={stats.fake} tone="red" />
        <StatCard icon={CheckCircle2} label="Có vẻ thật" value={stats.real} tone="green" />
        <StatCard icon={SlidersHorizontal} label="Tin cậy trung bình" value={`${stats.avgConfidence}%`} tone="yellow" />
      </section>

      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-shield-line bg-slate-950/35 p-5">
          <div className="flex items-center gap-2">
            <Clock className="text-shield-cyan" />
            <h2 className="text-lg font-semibold text-white">Các lần phân tích gần đây</h2>
          </div>

          <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row md:items-center">
            <label className="relative block md:w-72">
              <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Tìm theo tên file hoặc mã phân tích"
                className="w-full rounded-lg border border-shield-line bg-slate-950/60 py-2 pl-9 pr-3 text-sm text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-cyan-400/50"
              />
            </label>

            <div className="flex rounded-lg border border-shield-line bg-slate-950/60 p-1">
              {filters.map((filter) => (
                <button
                  key={filter.id}
                  type="button"
                  onClick={() => setActiveFilter(filter.id)}
                  className={`rounded-md px-3 py-1.5 text-sm font-semibold transition ${
                    activeFilter === filter.id ? "bg-cyan-400 text-slate-950" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-5">
          {loading && <HistorySkeleton />}
          {error && (
            <div className="rounded-xl border border-red-400/25 bg-red-400/[0.06] p-4 text-sm text-red-200">
              {error}
            </div>
          )}
          {!loading && !error && filteredHistory.length === 0 && (
            <div className="rounded-xl border border-shield-line bg-slate-950/45 p-8 text-center">
              <FileVideo className="mx-auto text-slate-500" size={38} />
              <p className="mt-3 font-semibold text-white">Chưa có mục phù hợp</p>
              <p className="mt-1 text-sm text-slate-500">Thử đổi bộ lọc hoặc tải tệp mới để phân tích.</p>
            </div>
          )}

          {!loading && !error && filteredHistory.length > 0 && (
            <div className="space-y-3">
              {filteredHistory.map((item) => (
                <HistoryItem key={item.analysisId} item={item} />
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

function HistoryItem({ item }) {
  const fake = isFake(item.prediction);
  const confidence = Math.round(Number(item.confidence) || 0);
  const risk = riskFromItem(item);
  const Icon = fake ? ShieldAlert : CheckCircle2;

  const openResult = () => {
    localStorage.setItem("latestAnalysisResult", JSON.stringify(item));
    window.location.hash = "#/results";
  };

  return (
    <button
      type="button"
      onClick={openResult}
      className="group w-full rounded-xl border border-shield-line bg-slate-950/55 p-4 text-left transition hover:border-cyan-400/40 hover:bg-slate-950/80"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          <div className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${fake ? "bg-red-400/10 text-red-200" : "bg-emerald-400/10 text-emerald-200"}`}>
            <Icon size={22} />
          </div>
          <div className="min-w-0">
            <p className="truncate font-semibold text-white">{item.fileName || item.analysisId}</p>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <span>{formatDate(item.createdAt)}</span>
              <span className="hidden h-1 w-1 rounded-full bg-slate-700 sm:inline-block" />
              <span>{item.analysisId}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge tone={fake ? "red" : "green"}>{fake ? "Nghi giả" : "Có vẻ thật"}</Badge>
          <Badge tone={risk.tone}>Rủi ro {risk.label}</Badge>
          <div className="w-28 text-right">
            <p className="text-sm font-semibold text-slate-200">{confidence}%</p>
            <div className="mt-1 h-2 rounded-full bg-slate-800">
              <div className={`h-2 rounded-full ${fake ? "bg-red-400" : "bg-emerald-400"}`} style={{ width: `${Math.max(4, Math.min(100, confidence))}%` }} />
            </div>
          </div>
        </div>
      </div>
    </button>
  );
}

function StatCard({ icon: Icon, label, value, tone }) {
  const tones = {
    cyan: "border-cyan-400/25 bg-cyan-400/[0.04] text-cyan-200",
    red: "border-red-400/25 bg-red-400/[0.04] text-red-200",
    green: "border-emerald-400/25 bg-emerald-400/[0.04] text-emerald-200",
    yellow: "border-yellow-400/25 bg-yellow-400/[0.04] text-yellow-200",
  };

  return (
    <Card className={`p-5 ${tones[tone] || tones.cyan}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-bold text-white">{value}</p>
        </div>
        <div className="rounded-lg border border-current/25 bg-slate-950/30 p-2">
          <Icon size={20} />
        </div>
      </div>
    </Card>
  );
}

function HistorySkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index} className="h-20 animate-pulse rounded-xl border border-shield-line bg-slate-950/50" />
      ))}
    </div>
  );
}

function Badge({ tone, children }) {
  const tones = {
    red: "border-red-400/30 bg-red-400/10 text-red-200",
    green: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
    yellow: "border-yellow-400/30 bg-yellow-400/10 text-yellow-200",
    cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
  };

  return (
    <span className={`hidden rounded-full border px-3 py-1 text-xs font-semibold sm:inline-flex ${tones[tone] || tones.cyan}`}>
      {children}
    </span>
  );
}

function isFake(prediction = "") {
  const value = String(prediction).toLowerCase();
  return value.includes("fake") || value.includes("manipulated") || value.includes("giả");
}

function isReal(prediction = "") {
  const value = String(prediction).toLowerCase();
  return value.includes("real") || value.includes("authentic") || value.includes("thật");
}

function riskFromItem(item) {
  const score = Number(item.riskScore) || Number(item.confidence) || 0;
  if (score >= 70) return { label: "cao", tone: "red" };
  if (score >= 45) return { label: "trung bình", tone: "yellow" };
  return { label: "thấp", tone: "cyan" };
}

function formatDate(value) {
  if (!value) return "Không rõ thời gian";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("vi-VN");
}

export default HistoryPage;
