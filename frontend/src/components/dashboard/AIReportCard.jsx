import { Brain, FileText, Lightbulb } from "lucide-react";

import Card from "../common/Card.jsx";

function AIReportCard({ report, reportId }) {
  return (
    <Card className="overflow-hidden">
      <div className="border-b border-shield-line bg-slate-950/35 p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Brain className="text-shield-cyan" />
            <h3 className="text-lg font-semibold text-white">Báo cáo giải thích AI</h3>
          </div>
          {reportId && (
            <a href="#/reports" className="inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-sm font-semibold text-cyan-200">
              <FileText size={16} />
              {reportId}
            </a>
          )}
        </div>
      </div>

      <div className="p-5">
        <div className="mb-4 flex gap-3 rounded-xl border border-cyan-400/20 bg-cyan-400/[0.04] p-4">
          <Lightbulb className="mt-0.5 text-cyan-300" size={20} />
          <p className="text-sm leading-6 text-slate-300">
            Báo cáo này giải thích theo hướng hỗ trợ điều tra: xem kết luận, mức rủi ro, vùng nghi ngờ và tín hiệu theo thời gian cùng nhau.
          </p>
        </div>
        <p className="whitespace-pre-line leading-7 text-slate-300">
          {report || "Chưa có nội dung báo cáo cho lần phân tích này."}
        </p>
      </div>
    </Card>
  );
}

export default AIReportCard;
