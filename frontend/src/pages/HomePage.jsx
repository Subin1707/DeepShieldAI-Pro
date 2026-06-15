import {
  ArrowRight,
  BarChart3,
  Brain,
  FileSearch,
  Flame,
  MessageSquareText,
  Radar,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";

const capabilities = [
  {
    icon: UploadCloud,
    title: "Tải video nghi vấn",
    text: "Hỗ trợ ảnh và video, tự tách frame, crop khuôn mặt và chuẩn bị chuỗi phân tích.",
  },
  {
    icon: Brain,
    title: "Phân tích theo thời gian",
    text: "Mô hình video temporal đánh giá nhiều frame liên tiếp thay vì nhìn một ảnh đơn lẻ.",
  },
  {
    icon: Radar,
    title: "Khoanh vùng nghi ngờ",
    text: "Làm nổi bật vùng mắt, miệng, mũi, viền mặt và giải thích vì sao đáng kiểm tra.",
  },
  {
    icon: MessageSquareText,
    title: "Chatbot giải thích",
    text: "Hỏi trực tiếp về kết luận, độ tin cậy, mức rủi ro và cách kiểm tra thủ công.",
  },
];

const workflow = [
  "Tải video hoặc ảnh cần kiểm tra",
  "AI phân tích chuỗi frame và vùng khuôn mặt",
  "Xem kết luận, heatmap, điểm nghi ngờ và báo cáo tiếng Việt",
];

function HomePage() {
  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-lg border border-shield-line bg-shield-panel shadow-glow">
        <div className="grid gap-6 p-6 lg:grid-cols-[1fr_24rem] lg:p-8">
          <div className="max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
              <ShieldCheck size={16} />
              Nền tảng điều tra Deepfake bằng AI
            </div>
            <h2 className="text-4xl font-bold tracking-tight text-white">DeepShield AI Pro</h2>
            <p className="mt-4 text-lg leading-8 text-slate-300">
              Phân tích video nghi vấn, khoanh vùng các điểm bất thường trên khuôn mặt và tạo báo cáo giải thích
              bằng tiếng Việt để hỗ trợ kiểm chứng thủ công.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href="#/upload"
                className="inline-flex items-center gap-2 rounded-lg bg-cyan-400 px-5 py-3 font-semibold text-slate-950 hover:bg-cyan-300"
              >
                Bắt đầu phân tích
                <ArrowRight size={18} />
              </a>
              <a
                href="#/results"
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-5 py-3 font-semibold text-slate-200 hover:border-cyan-400/50 hover:text-white"
              >
                Xem kết quả gần nhất
                <BarChart3 size={18} />
              </a>
            </div>
          </div>

          <div className="rounded-lg border border-cyan-400/20 bg-slate-950/60 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Trạng thái hệ thống</p>
                <p className="mt-1 text-xl font-bold text-white">Sẵn sàng phân tích</p>
              </div>
              <Flame className="text-shield-cyan" size={28} />
            </div>
            <div className="mt-5 space-y-3">
              <StatusRow label="Backend FastAPI" value="Đang chạy" tone="success" />
              <StatusRow label="Mô hình video" value="Đã tích hợp" tone="info" />
              <StatusRow label="Heatmap" value="Có giải thích vùng nghi ngờ" tone="info" />
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        {capabilities.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.title} className="rounded-lg border border-shield-line bg-shield-panel p-5">
              <Icon className="mb-4 text-shield-cyan" size={26} />
              <h3 className="font-semibold text-white">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-400">{item.text}</p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_22rem]">
        <div className="rounded-lg border border-shield-line bg-shield-panel p-6">
          <div className="mb-5 flex items-center gap-2">
            <FileSearch className="text-shield-cyan" />
            <h3 className="text-lg font-semibold text-white">Quy trình kiểm tra</h3>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {workflow.map((step, index) => (
              <div key={step} className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-cyan-400 text-sm font-bold text-slate-950">
                  {index + 1}
                </span>
                <p className="mt-3 text-sm leading-6 text-slate-300">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-shield-line bg-shield-panel p-6">
          <h3 className="text-lg font-semibold text-white">Lưu ý điều tra</h3>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Kết quả AI là tín hiệu hỗ trợ, không phải kết luận tuyệt đối. Với video mờ, nén mạnh hoặc khuôn mặt quá nhỏ,
            nên xem thêm heatmap, các đoạn frame nghi ngờ và kiểm tra thủ công.
          </p>
        </div>
      </section>
    </div>
  );
}

function StatusRow({ label, value, tone }) {
  const toneClass = tone === "success" ? "text-green-300" : "text-cyan-300";

  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/70 px-3 py-2">
      <span className="text-sm text-slate-400">{label}</span>
      <span className={`text-sm font-semibold ${toneClass}`}>{value}</span>
    </div>
  );
}

export default HomePage;
