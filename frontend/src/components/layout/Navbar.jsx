import { Activity, Menu, Shield, Sparkles, X } from "lucide-react";

function Navbar({ sidebarOpen = false, onToggleSidebar }) {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-cyan-400/25 bg-[linear-gradient(90deg,rgba(2,6,23,0.96),rgba(8,13,30,0.92),rgba(2,6,23,0.96))] shadow-[0_14px_50px_rgba(2,6,23,0.58)] backdrop-blur-xl">
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-300/70 to-transparent" />
      <div className="pointer-events-none absolute left-16 top-0 h-16 w-72 bg-cyan-400/10 blur-3xl" />
      <div className="pointer-events-none absolute right-24 top-0 h-16 w-72 bg-emerald-400/10 blur-3xl" />

      <div className="relative flex h-16 items-center justify-between px-4 lg:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onToggleSidebar}
            className="rounded-lg border border-slate-700 p-2 text-slate-300 transition hover:border-cyan-400/60 hover:bg-cyan-400/10 hover:text-cyan-200 lg:hidden"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div className="flex min-w-0 items-center gap-3">
            <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-cyan-300/45 bg-gradient-to-br from-cyan-400/20 via-blue-500/12 to-violet-500/18 shadow-[0_0_22px_rgba(25,230,255,0.16)]">
              <div className="absolute inset-0 rounded-xl bg-cyan-300/10 opacity-0 transition hover:opacity-100" />
              <Shield className="relative text-shield-cyan" size={24} />
            </div>
            <div className="min-w-0 leading-tight">
              <h1 className="truncate text-lg font-extrabold tracking-tight text-white">DeepShield AI Pro</h1>
              <p className="hidden truncate text-xs text-slate-400 sm:block">Nền tảng điều tra Deepfake</p>
            </div>
            <span className="hidden rounded-full border border-violet-300/25 bg-violet-400/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.16em] text-violet-100 md:inline-flex">
              Forensics
            </span>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-cyan-400/20 bg-slate-950/55 px-3 py-1.5 text-xs text-cyan-100 lg:flex">
            <Sparkles size={14} className="text-cyan-300" />
            AI Forensics Console
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-400/40 bg-emerald-400/12 px-3 py-1.5 text-sm font-semibold text-emerald-100 shadow-[0_0_26px_rgba(52,211,153,0.16)]">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-60" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-300" />
            </span>
            <Activity size={15} />
            <span>Backend sẵn sàng</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
