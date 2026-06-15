import { FileUp, ShieldCheck, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

function UploadBox({ file, onFileSelect, disabled = false }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const selectFile = (selectedFile) => {
    if (selectedFile && !disabled) {
      onFileSelect(selectedFile);
    }
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border-2 border-dashed p-8 text-center transition ${
        dragging ? "border-cyan-300 bg-cyan-400/10 shadow-glow" : "border-cyan-400/30 bg-slate-950/50"
      } ${disabled ? "opacity-70" : "cursor-pointer hover:border-cyan-300/70 hover:bg-cyan-400/5"}`}
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
      }}
      onDragEnter={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        selectFile(event.dataTransfer.files?.[0]);
      }}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(34,211,238,0.11),transparent_42%)]" />
      <div className="relative">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/25 bg-cyan-400/10 text-shield-cyan">
          {file ? <FileUp size={30} /> : <UploadCloud size={32} />}
        </div>
        <p className="mt-4 text-lg font-semibold text-white">
          {file ? file.name : "Kéo thả tệp vào đây hoặc bấm để chọn"}
        </p>
        <p className="mt-2 text-sm text-slate-400">Hỗ trợ JPG, PNG, WEBP, MP4, AVI, MOV, MKV</p>
        <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1 text-xs text-cyan-100">
          <ShieldCheck size={14} />
          Nên dùng video có khuôn mặt rõ, ít rung và đủ ánh sáng
        </div>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/*,video/*"
        className="hidden"
        disabled={disabled}
        onChange={(event) => selectFile(event.target.files?.[0])}
      />
    </div>
  );
}

export default UploadBox;
