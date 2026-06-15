import {
  BarChart3,
  CheckCircle2,
  FileText,
  History,
  Home,
  Info,
  MessageSquare,
  Shield,
  UploadCloud,
} from "lucide-react";

const navItems = [
  { label: "Trang chủ", description: "Tổng quan hệ thống", href: "#/", icon: Home },
  { label: "Tải lên", description: "Gửi ảnh hoặc video", href: "#/upload", icon: UploadCloud },
  { label: "Kết quả", description: "Heatmap và báo cáo", href: "#/results", icon: BarChart3 },
  { label: "Lịch sử", description: "Các lần phân tích", href: "#/history", icon: History },
  { label: "Báo cáo", description: "Tải báo cáo", href: "#/reports", icon: FileText },
  { label: "Chatbot", description: "Hỏi AI giải thích", href: "#/chatbot", icon: MessageSquare },
  { label: "Giới thiệu", description: "Thông tin dự án", href: "#/about", icon: Info },
];

function Sidebar({ open = false, activePath = "#/", onNavigate }) {
  return (
    <>
      {open && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onNavigate}
          aria-label="Close sidebar"
        />
      )}

      <aside
        className={`fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-72 overflow-hidden border-r border-cyan-400/15 bg-slate-950/88 shadow-[20px_0_50px_rgba(2,6,23,0.35)] backdrop-blur-xl transition-transform lg:fixed lg:top-16 lg:z-30 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col overflow-y-auto overscroll-contain p-4 pr-3 [scrollbar-color:rgba(34,211,238,0.55)_rgba(15,23,42,0.75)] [scrollbar-width:thin]">
          <div className="mb-4 rounded-xl border border-cyan-400/25 bg-[radial-gradient(circle_at_top_right,rgba(25,230,255,0.18),transparent_45%),linear-gradient(135deg,rgba(8,47,73,0.55),rgba(15,23,42,0.86))] p-4 shadow-glow">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-300/45 bg-cyan-400/12">
                <Shield className="text-shield-cyan" size={22} />
              </div>
              <div>
                <p className="font-semibold text-white">DeepShield</p>
                <p className="text-xs text-cyan-100/70">AI Forensics Console</p>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-emerald-400/25 bg-emerald-400/12 px-3 py-2 text-xs text-emerald-200">
              <CheckCircle2 size={14} />
              Hệ thống sẵn sàng
            </div>
          </div>

          <nav className="space-y-2 pb-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = activePath === item.href;

              return (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={onNavigate}
                  className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                    active
                      ? "border border-cyan-300/45 bg-gradient-to-r from-cyan-400/18 to-violet-500/12 text-cyan-50 shadow-glow"
                      : "text-slate-400 hover:bg-slate-900/85 hover:text-white"
                  }`}
                >
                  <div
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                      active ? "bg-cyan-400/18 text-cyan-100" : "bg-slate-900 text-slate-400"
                    }`}
                  >
                    <Icon size={18} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold">{item.label}</p>
                    <p className={`mt-0.5 text-xs ${active ? "text-cyan-100/70" : "text-slate-500"}`}>
                      {item.description}
                    </p>
                  </div>
                </a>
              );
            })}
          </nav>

          <div className="mt-auto space-y-3 pt-3">
            <div className="rounded-xl border border-violet-400/20 bg-[linear-gradient(135deg,rgba(15,23,42,0.9),rgba(76,29,149,0.18))] p-4">
              <p className="text-sm font-semibold text-white">Chế độ phân tích</p>
              <p className="mt-2 text-xs leading-5 text-slate-400">
                Ưu tiên mô hình video temporal. Nếu model không khả dụng, hệ thống dùng phân tích fallback.
              </p>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                <div className="h-full w-4/5 rounded-full bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400" />
              </div>
              <p className="mt-2 text-xs text-cyan-200">Video model + heatmap giải thích</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
