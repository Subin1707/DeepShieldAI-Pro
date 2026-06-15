import { useEffect, useMemo, useState } from "react";
import {
  CalendarClock,
  Download,
  FileArchive,
  FileCheck2,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import Card from "../components/common/Card.jsx";
import { getReportDownloadUrl, getReports } from "../services/reportService";

function ReportPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  const loadReports = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getReports();
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Không tải được danh sách báo cáo.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const sortedReports = useMemo(() => {
    return [...reports].sort((a, b) => reportTime(b.reportId) - reportTime(a.reportId));
  }, [reports]);

  const filteredReports = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return sortedReports;

    return sortedReports.filter((report) =>
      `${report.reportId || ""} ${report.fileName || ""}`.toLowerCase().includes(keyword),
    );
  }, [query, sortedReports]);

  const latestReport = sortedReports[0];

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-cyan-400/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.13),transparent_32%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(2,6,23,0.98))] p-6">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              <Sparkles size={14} />
              Kho báo cáo điều tra
            </div>
            <h1 className="text-3xl font-bold text-white">Báo cáo</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
              Quản lý các báo cáo AI đã tạo, tìm lại hồ sơ theo mã hoặc tên tệp và tải xuống để lưu trữ hoặc đối chiếu.
            </p>
          </div>

          <button
            type="button"
            onClick={loadReports}
            className="inline-flex items-center gap-2 rounded-lg border border-cyan-400/25 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            Làm mới
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <StatCard icon={FileArchive} label="Tổng báo cáo" value={reports.length} tone="cyan" />
        <StatCard icon={CalendarClock} label="Mới nhất" value={latestReport ? formatReportDate(latestReport.reportId) : "Chưa có"} tone="green" />
        <StatCard icon={ShieldCheck} label="Trạng thái" value={reports.length ? "Sẵn sàng tải" : "Đang trống"} tone="yellow" />
      </section>

      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-shield-line bg-slate-950/35 p-5">
          <div className="flex items-center gap-2">
            <FileText className="text-shield-cyan" />
            <h2 className="text-lg font-semibold text-white">Danh sách báo cáo</h2>
          </div>

          <label className="relative block w-full md:w-80">
            <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Tìm theo mã báo cáo hoặc tên file"
              className="w-full rounded-lg border border-shield-line bg-slate-950/60 py-2 pl-9 pr-3 text-sm text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-cyan-400/50"
            />
          </label>
        </div>

        <div className="p-5">
          {loading && <ReportSkeleton />}
          {error && (
            <div className="rounded-xl border border-red-400/25 bg-red-400/[0.06] p-4 text-sm text-red-200">
              {error}
            </div>
          )}
          {!loading && !error && filteredReports.length === 0 && (
            <div className="rounded-xl border border-shield-line bg-slate-950/45 p-8 text-center">
              <FileText className="mx-auto text-slate-500" size={38} />
              <p className="mt-3 font-semibold text-white">Chưa có báo cáo phù hợp</p>
              <p className="mt-1 text-sm text-slate-500">Hãy tạo phân tích mới hoặc đổi từ khóa tìm kiếm.</p>
            </div>
          )}

          {!loading && !error && filteredReports.length > 0 && (
            <div className="grid gap-4 xl:grid-cols-2">
              {filteredReports.map((report) => (
                <ReportCard key={report.reportId} report={report} />
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

function ReportCard({ report }) {
  const fileName = report.fileName || `${report.reportId}.txt`;

  return (
    <article className="group rounded-xl border border-shield-line bg-slate-950/55 p-5 transition hover:border-cyan-400/40 hover:bg-slate-950/80">
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 gap-4">
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-200">
            <FileCheck2 size={22} />
          </div>
          <div className="min-w-0">
            <p className="truncate font-semibold text-white">{report.reportId}</p>
            <p className="mt-1 truncate text-sm text-slate-500" title={fileName}>
              {fileName}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge>{formatReportDate(report.reportId)}</Badge>
              <Badge>TXT report</Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-shield-line pt-4">
        <p className="text-xs leading-5 text-slate-500">
          Báo cáo chứa kết luận, độ tin cậy, vùng nghi ngờ và khuyến nghị kiểm tra thủ công.
        </p>
        <a
          href={getReportDownloadUrl(report.reportId)}
          className="inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
        >
          <Download size={16} />
          Tải xuống
        </a>
      </div>
    </article>
  );
}

function StatCard({ icon: Icon, label, value, tone }) {
  const tones = {
    cyan: "border-cyan-400/25 bg-cyan-400/[0.04] text-cyan-200",
    green: "border-emerald-400/25 bg-emerald-400/[0.04] text-emerald-200",
    yellow: "border-yellow-400/25 bg-yellow-400/[0.04] text-yellow-200",
  };

  return (
    <Card className={`p-5 ${tones[tone] || tones.cyan}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold text-white">{value}</p>
        </div>
        <div className="rounded-lg border border-current/25 bg-slate-950/30 p-2">
          <Icon size={20} />
        </div>
      </div>
    </Card>
  );
}

function Badge({ children }) {
  return (
    <span className="rounded-full border border-cyan-400/20 bg-cyan-400/[0.06] px-3 py-1 text-xs font-semibold text-cyan-200">
      {children}
    </span>
  );
}

function ReportSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="h-36 animate-pulse rounded-xl border border-shield-line bg-slate-950/50" />
      ))}
    </div>
  );
}

function reportTime(reportId = "") {
  const match = String(reportId).match(/RPT-(\d{8})-/);
  if (!match) return 0;
  const year = match[1].slice(0, 4);
  const month = match[1].slice(4, 6);
  const day = match[1].slice(6, 8);
  return new Date(`${year}-${month}-${day}T00:00:00`).getTime();
}

function formatReportDate(reportId = "") {
  const match = String(reportId).match(/RPT-(\d{8})-/);
  if (!match) return "Không rõ ngày";
  const year = match[1].slice(0, 4);
  const month = match[1].slice(4, 6);
  const day = match[1].slice(6, 8);
  const date = new Date(`${year}-${month}-${day}T00:00:00`);
  return date.toLocaleDateString("vi-VN");
}

export default ReportPage;
