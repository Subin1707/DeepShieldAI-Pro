import { FileVideo, Image as ImageIcon, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

function formatBytes(bytes = 0) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function FilePreview({ file, onClear }) {
  const [url, setUrl] = useState("");
  const isVideo = file?.type?.startsWith("video/");
  const isImage = file?.type?.startsWith("image/");

  useEffect(() => {
    if (!file) return undefined;
    const objectUrl = URL.createObjectURL(file);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [file]);

  const meta = useMemo(() => {
    if (!file) return [];
    return [
      file.type || "Không rõ định dạng",
      formatBytes(file.size),
      new Date(file.lastModified).toLocaleString("vi-VN"),
    ];
  }, [file]);

  if (!file) return null;

  return (
    <div className="mt-6 overflow-hidden rounded-2xl border border-shield-line bg-slate-950/60">
      <div className="flex items-center justify-between gap-4 border-b border-shield-line px-4 py-3">
        <div className="min-w-0">
          <p className="truncate font-semibold text-white">{file.name}</p>
          <p className="mt-1 text-xs text-slate-500">{meta.join(" | ")}</p>
        </div>
        {onClear && (
          <button type="button" onClick={onClear} className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-white">
            <X size={18} />
          </button>
        )}
      </div>

      <div className="flex min-h-56 items-center justify-center bg-black p-2">
        {isImage && <img src={url} alt={file.name} className="max-h-96 w-auto max-w-full object-contain" />}
        {isVideo && <video src={url} controls className="max-h-96 w-full rounded-lg bg-black" />}
        {!isImage && !isVideo && (
          <div className="p-8 text-center text-slate-400">
            <FileVideo className="mx-auto text-shield-cyan" size={40} />
            <p className="mt-3">Chưa hỗ trợ xem trước loại tệp này.</p>
          </div>
        )}
        {isImage === false && isVideo === false && <ImageIcon className="hidden" />}
      </div>
    </div>
  );
}

export default FilePreview;
