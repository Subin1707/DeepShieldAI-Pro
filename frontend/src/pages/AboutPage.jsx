import {
  Activity,
  Brain,
  CheckCircle2,
  Cpu,
  Database,
  FileText,
  Gauge,
  Layers3,
  Radar,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from "lucide-react";

import Card from "../components/common/Card.jsx";

const capabilities = [
  {
    icon: UploadCloud,
    title: "Tiếp nhận ảnh và video",
    text: "Hỗ trợ tải lên tệp nghi vấn, lưu trữ backend và chuẩn bị dữ liệu cho pipeline phân tích.",
  },
  {
    icon: Brain,
    title: "Phân tích học sâu",
    text: "Ưu tiên mô hình video temporal đã train, sau đó dùng mô hình frame hoặc fallback pháp chứng khi model không khả dụng.",
  },
  {
    icon: Radar,
    title: "Bản đồ vùng nghi ngờ",
    text: "Sinh heatmap, khoanh vùng mắt, miệng, viền khuôn mặt và các điểm saliency cần kiểm tra thủ công.",
  },
  {
    icon: FileText,
    title: "Báo cáo tiếng Việt",
    text: "Tạo báo cáo điều tra có giải thích, mức rủi ro, tín hiệu phát hiện và khuyến nghị kiểm tra.",
  },
];

const stack = [
  { label: "Backend", value: "FastAPI, OpenCV, SQLite, TensorFlow/Keras" },
  { label: "Frontend", value: "React, Vite, Tailwind CSS, Axios, Lucide" },
  { label: "AI", value: "EfficientNet/frame model, video temporal model, forensic fallback" },
  { label: "Báo cáo", value: "Groq/Gemini API hoặc fallback tiếng Việt nội bộ" },
];

const pipeline = [
  "Tải tệp và kiểm tra định dạng",
  "Trích xuất metadata, frame và khuôn mặt",
  "Chạy mô hình deep learning hoặc fallback pháp chứng",
  "Sinh heatmap và vùng nghi ngờ",
  "Tạo báo cáo, lưu lịch sử và hỗ trợ chatbot giải thích",
];

function AboutPage() {
  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-xl border border-cyan-400/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.15),transparent_32%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(2,6,23,0.98))] p-6 lg:p-8">
        <div className="grid gap-8 lg:grid-cols-[1.25fr_0.75fr]">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
              <Sparkles size={14} />
              DeepShield AI Forensics Console
            </div>
            <h1 className="text-3xl font-bold text-white md:text-4xl">Nền tảng hỗ trợ điều tra Deepfake</h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300 md:text-base">
              DeepShield AI Pro là hệ thống full-stack dùng để phân tích ảnh/video nghi vấn, hiển thị kết luận mô hình, bản đồ vùng nghi ngờ, lịch sử phân tích và báo cáo giải thích bằng tiếng Việt. Mục tiêu là hỗ trợ điều tra, không thay thế kết luận pháp lý cuối cùng.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <StatusPill icon={CheckCircle2} label="Backend sẵn sàng" />
              <StatusPill icon={Brain} label="Video temporal model" />
              <StatusPill icon={Radar} label="Heatmap giải thích" />
            </div>
          </div>

          <Card className="p-5">
            <div className="flex items-center gap-2">
              <Gauge className="text-shield-cyan" />
              <h2 className="font-semibold text-white">Trạng thái năng lực</h2>
            </div>
            <div className="mt-5 space-y-4">
              <CapabilityMeter label="Pipeline phân tích" value={92} />
              <CapabilityMeter label="Giải thích vùng nghi ngờ" value={88} />
              <CapabilityMeter label="Báo cáo tiếng Việt" value={90} />
            </div>
          </Card>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {capabilities.map((item) => (
          <InfoCard key={item.title} {...item} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <Layers3 className="text-shield-cyan" />
            <h2 className="text-lg font-semibold text-white">Luồng xử lý</h2>
          </div>
          <div className="space-y-3">
            {pipeline.map((step, index) => (
              <div key={step} className="flex gap-3 rounded-xl border border-shield-line bg-slate-950/45 p-4">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-cyan-400 text-sm font-bold text-slate-950">
                  {index + 1}
                </span>
                <p className="self-center text-sm font-medium text-slate-200">{step}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <Cpu className="text-shield-cyan" />
            <h2 className="text-lg font-semibold text-white">Công nghệ sử dụng</h2>
          </div>
          <div className="space-y-3">
            {stack.map((item) => (
              <div key={item.label} className="rounded-xl border border-shield-line bg-slate-950/45 p-4">
                <p className="text-sm font-semibold text-white">{item.label}</p>
                <p className="mt-1 text-sm leading-6 text-slate-400">{item.value}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="p-6">
          <div className="mb-4 flex items-center gap-2">
            <Database className="text-shield-cyan" />
            <h2 className="text-lg font-semibold text-white">Dữ liệu và lưu trữ</h2>
          </div>
          <p className="text-sm leading-7 text-slate-400">
            Hệ thống lưu lịch sử phân tích, báo cáo dạng JSON/TXT, heatmap và metadata phục vụ việc xem lại kết quả. Tệp huấn luyện lớn nên được đặt ngoài repo, ví dụ ổ dữ liệu riêng, sau đó truyền đường dẫn vào script train.
          </p>
        </Card>

        <Card className="border-yellow-400/25 bg-yellow-400/[0.04] p-6">
          <div className="mb-4 flex items-center gap-2">
            <Activity className="text-yellow-300" />
            <h2 className="text-lg font-semibold text-white">Giới hạn cần nhớ</h2>
          </div>
          <ul className="space-y-2 text-sm leading-6 text-slate-300">
            <li>Không nên kết luận tuyệt đối chỉ dựa vào một lần phân tích.</li>
            <li>Video mờ, nén mạnh hoặc mặt quá nhỏ có thể làm heatmap và dự đoán kém ổn định.</li>
            <li>Để tăng độ chính xác cần tiếp tục train/fine-tune model bằng dữ liệu cân bằng và kiểm thử độc lập.</li>
          </ul>
        </Card>
      </section>
    </div>
  );
}

function InfoCard({ icon: Icon, title, text }) {
  return (
    <Card className="p-5">
      <div className="mb-4 grid h-11 w-11 place-items-center rounded-xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-200">
        <Icon size={22} />
      </div>
      <h3 className="font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-400">{text}</p>
    </Card>
  );
}

function StatusPill({ icon: Icon, label }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-2 text-xs font-semibold text-cyan-100">
      <Icon size={14} />
      {label}
    </span>
  );
}

function CapabilityMeter({ label, value }) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-semibold text-cyan-200">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-slate-800">
        <div className="h-2 rounded-full bg-cyan-400" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default AboutPage;
