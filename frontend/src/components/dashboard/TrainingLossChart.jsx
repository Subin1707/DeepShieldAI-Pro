import { Activity, LineChart, Sigma } from "lucide-react";

import Card from "../common/Card.jsx";

function TrainingLossChart({ result = {} }) {
  const { points, latestPoints, source, runCount, runId, validationReport } = getTrainingHistory(result);
  const hasHistory = points.length >= 2;
  const chart = hasHistory ? buildChart(points) : null;
  const latestLastPoint = latestPoints[latestPoints.length - 1] || points[points.length - 1] || {};
  const bestPoint = points.reduce(
    (best, point) => (Number(point.valLoss ?? point.loss) < Number(best.valLoss ?? best.loss) ? point : best),
    points[0] || {},
  );

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-shield-line bg-slate-950/35 p-5">
        <div className="flex items-center gap-2">
          <LineChart className="text-shield-cyan" />
          <div>
            <h3 className="text-lg font-semibold text-white">Training / validation loss</h3>
            <p className="mt-1 text-xs text-slate-400">Tong hop tat ca run, dong thoi tach rieng run moi nhat.</p>
          </div>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-100">
          <Activity size={14} />
          {hasHistory ? `${runCount || 1} run` : "Chua co log"}
        </span>
      </div>

      <div className="grid gap-5 p-5 xl:grid-cols-[minmax(0,1fr)_16rem]">
        <div className="rounded-lg border border-shield-line bg-[#f7f7f2] p-3 text-slate-900">
          {hasHistory ? <MatlabLossFigure chart={chart} /> : <MissingHistory />}
        </div>

        <aside className="space-y-3">
          <Stat icon={Sigma} label="Tong diem train" value={points.length} />
          <Stat icon={Activity} label="Run moi nhat" value={runId || "latest"} />
          <Stat icon={Activity} label="Epoch run moi" value={latestPoints.length || points.length} />
          <Stat icon={LineChart} label="Train loss moi nhat" value={formatLoss(latestLastPoint.loss)} />
          <Stat icon={Activity} label="Val loss tot nhat" value={formatLoss(bestPoint.valLoss ?? bestPoint.loss)} />
          <ValidationSummary report={validationReport} />
          <div className="rounded-lg border border-shield-line bg-slate-950/45 p-4 text-sm leading-6 text-slate-400">
            {hasHistory
              ? `Du lieu lay tu log train that: ${source || "trainingHistory"}`
              : "Bieu do chi hien khi backend tra ve trainingHistory co loss that."}
          </div>
        </aside>
      </div>
    </Card>
  );
}

function MatlabLossFigure({ chart }) {
  return (
    <svg viewBox="0 0 720 360" className="h-auto w-full" role="img" aria-label="Training loss chart">
      <rect x="0" y="0" width="720" height="360" fill="#f7f7f2" />
      {chart.yTicks.map((tick) => (
        <g key={`y-${tick.value}`}>
          <line x1="70" y1={tick.y} x2="675" y2={tick.y} stroke="#d4d4cc" strokeWidth="1" />
          <text x="58" y={tick.y + 4} textAnchor="end" fontSize="12" fill="#0f2a44">
            {tick.value.toFixed(2)}
          </text>
        </g>
      ))}
      {chart.xTicks.map((tick) => (
        <g key={`x-${tick.value}`}>
          <line x1={tick.x} y1="42" x2={tick.x} y2="302" stroke="#e2e2d8" strokeWidth="1" />
          <text x={tick.x} y="324" textAnchor="middle" fontSize="12" fill="#0f2a44">
            {tick.value}
          </text>
        </g>
      ))}
      {chart.runBreaks.map((mark) => (
        <g key={`run-${mark.step}`}>
          <line x1={mark.x} y1="42" x2={mark.x} y2="302" stroke="#64748b" strokeDasharray="5 5" strokeWidth="1.2" />
          <text x={mark.x + 5} y="56" fontSize="10" fill="#475569">{mark.label}</text>
        </g>
      ))}

      <line x1="70" y1="302" x2="675" y2="302" stroke="#111827" strokeWidth="1.7" />
      <line x1="70" y1="42" x2="70" y2="302" stroke="#111827" strokeWidth="1.7" />
      <text x="372" y="348" textAnchor="middle" fontSize="14" fontWeight="700" fill="#111827">
        Global training step
      </text>
      <text x="20" y="176" textAnchor="middle" fontSize="14" fontWeight="700" fill="#111827" transform="rotate(-90 20 176)">
        Loss
      </text>
      <text x="372" y="24" textAnchor="middle" fontSize="16" fontWeight="700" fill="#020617">
        All Runs Training / Validation Loss
      </text>

      <path d={chart.lossPath} fill="none" stroke="#0057b8" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
      {chart.valLossPath && (
        <path d={chart.valLossPath} fill="none" stroke="#d71920" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
      )}

      {chart.lossPoints.map((point) => (
        <circle key={`loss-${point.step}`} cx={point.x} cy={point.y} r="4" fill="#0057b8" />
      ))}
      {chart.valLossPoints.map((point) => (
        <circle key={`val-${point.step}`} cx={point.x} cy={point.y} r="4" fill="#d71920" />
      ))}

      <g transform="translate(500 52)">
        <rect x="0" y="0" width="150" height={chart.valLossPath ? 48 : 28} fill="#ffffff" stroke="#94a3b8" />
        <line x1="12" y1="16" x2="42" y2="16" stroke="#0057b8" strokeWidth="3.2" />
        <text x="50" y="20" fontSize="12" fill="#111827">train loss</text>
        {chart.valLossPath && (
          <>
            <line x1="12" y1="36" x2="42" y2="36" stroke="#d71920" strokeWidth="3.2" />
            <text x="50" y="40" fontSize="12" fill="#111827">val loss</text>
          </>
        )}
      </g>
    </svg>
  );
}

function MissingHistory() {
  return (
    <div className="grid min-h-[22rem] place-items-center px-6 text-center">
      <div>
        <p className="text-lg font-bold text-slate-900">Chua co du lieu loss that</p>
        <p className="mt-2 max-w-xl text-sm leading-6 text-slate-600">
          Backend chua tra trainingHistory trong ket qua nay. Hay chay lai phan tich sau khi co file log train, hoac kiem tra TRAINING_HISTORY_PATH.
        </p>
      </div>
    </div>
  );
}

function getTrainingHistory(result) {
  const trainingHistory = result.trainingHistory;
  const history =
    trainingHistory?.points ||
    trainingHistory?.currentRun?.points ||
    trainingHistory ||
    result.trainingMetrics?.history ||
    result.modelTraining?.history ||
    result.trainingLoss;

  const points = normalizeHistory(history);
  const latestPoints = normalizeHistory(trainingHistory?.currentRun?.points);
  if (points.length >= 2) {
    return {
      points,
      latestPoints,
      source: trainingHistory?.source || "payload",
      runCount: trainingHistory?.runCount,
      runId: trainingHistory?.currentRun?.runId || points[0]?.runId,
      validationReport: trainingHistory?.validationReport,
    };
  }

  return { points: [], latestPoints: [], source: "", runCount: 0, runId: "", validationReport: null };
}

function normalizeHistory(history) {
  if (!history) return [];

  if (Array.isArray(history)) {
    return history
      .map((item, index) => ({
        step: Number(item.step ?? index + 1),
        runStep: Number(item.runStep ?? item.step ?? index + 1),
        epoch: Number(item.epoch ?? item.step ?? index + 1),
        runId: item.runId,
        loss: Number(item.loss ?? item.trainLoss ?? item.trainingLoss),
        valLoss: optionalNumber(item.valLoss ?? item.val_loss ?? item.validationLoss),
      }))
      .filter((item) => Number.isFinite(item.step) && Number.isFinite(item.loss));
  }

  const losses = history.loss || history.trainLoss || history.trainingLoss || [];
  const valLosses = history.valLoss || history.val_loss || history.validationLoss || [];
  if (!Array.isArray(losses)) return [];

  return losses
    .map((loss, index) => ({
      step: index + 1,
      runStep: index + 1,
      epoch: index + 1,
      loss: Number(loss),
      valLoss: optionalNumber(valLosses[index]),
    }))
    .filter((item) => Number.isFinite(item.loss));
}

function buildChart(points) {
  const plot = { left: 70, right: 675, top: 42, bottom: 302 };
  const losses = points.flatMap((point) => [point.loss, point.valLoss]).filter((value) => Number.isFinite(value));
  const maxLoss = Math.max(...losses, 1);
  const minLoss = Math.min(...losses, 0);
  const yMax = roundUp(maxLoss * 1.08);
  const yMin = Math.max(0, Math.floor(minLoss * 10 - 1) / 10);
  const stepMin = Math.min(...points.map((point) => point.step));
  const stepMax = Math.max(...points.map((point) => point.step));

  const scaleX = (step) => {
    if (stepMax === stepMin) return (plot.left + plot.right) / 2;
    return plot.left + ((step - stepMin) / (stepMax - stepMin)) * (plot.right - plot.left);
  };
  const scaleY = (loss) => plot.bottom - ((loss - yMin) / (yMax - yMin || 1)) * (plot.bottom - plot.top);

  const lossPoints = points.map((point) => ({ step: point.step, x: scaleX(point.step), y: scaleY(point.loss) }));
  const valLossPoints = points
    .filter((point) => Number.isFinite(point.valLoss))
    .map((point) => ({ step: point.step, x: scaleX(point.step), y: scaleY(point.valLoss) }));
  const runBreaks = points
    .map((point, index) => ({ point, previous: points[index - 1] }))
    .filter(({ point, previous }) => previous && point.runId && previous.runId && point.runId !== previous.runId)
    .map(({ point }) => ({
      step: point.step,
      x: scaleX(point.step),
      label: point.runId,
    }));

  return {
    lossPath: toPath(lossPoints, points),
    valLossPath: valLossPoints.length > 1 ? toPath(valLossPoints, points.filter((point) => Number.isFinite(point.valLoss))) : "",
    lossPoints,
    valLossPoints,
    runBreaks,
    xTicks: makeXTicks(stepMin, stepMax).map((value) => ({ value, x: scaleX(value) })),
    yTicks: makeYTicks(yMin, yMax).map((value) => ({ value, y: scaleY(value) })),
  };
}

function toPath(chartPoints, sourcePoints = chartPoints) {
  return chartPoints
    .map((point, index) => {
      const current = sourcePoints[index] || {};
      const previous = sourcePoints[index - 1] || {};
      const command = index === 0 || (current.runId && previous.runId && current.runId !== previous.runId) ? "M" : "L";
      return `${command} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`;
    })
    .join(" ");
}

function makeXTicks(min, max) {
  const count = Math.min(6, Math.max(2, max - min + 1));
  return Array.from({ length: count }, (_, index) => Math.round(min + (index / (count - 1)) * (max - min)));
}

function makeYTicks(min, max) {
  const count = 6;
  return Array.from({ length: count }, (_, index) => min + (index / (count - 1)) * (max - min));
}

function roundUp(value) {
  if (value <= 1) return Math.ceil(value * 10) / 10;
  return Math.ceil(value * 2) / 2;
}

function optionalNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : undefined;
}

function formatLoss(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "N/A";
  return number.toFixed(3);
}

function ValidationSummary({ report }) {
  if (!report) return null;

  const matrix = report.confusionMatrix || {};
  return (
    <div className="rounded-lg border border-shield-line bg-slate-950/45 p-4 text-sm text-slate-400">
      <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
        <Activity size={14} className="text-cyan-300" />
        Validation report
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="AUC" value={formatMetric(report.auc)} />
        <Metric label="Accuracy" value={formatPercent(report.accuracy)} />
        <Metric label="TP" value={matrix.tp ?? "N/A"} />
        <Metric label="FP" value={matrix.fp ?? "N/A"} />
        <Metric label="FN" value={matrix.fn ?? "N/A"} />
        <Metric label="TN" value={matrix.tn ?? "N/A"} />
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950/55 p-2">
      <p className="text-[0.68rem] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function formatMetric(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "N/A";
  return number.toFixed(3);
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "N/A";
  return `${Math.round(number * 100)}%`;
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-shield-line bg-slate-950/45 p-4">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
        <Icon size={14} className="text-cyan-300" />
        {label}
      </div>
      <p className="mt-2 text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

export default TrainingLossChart;
