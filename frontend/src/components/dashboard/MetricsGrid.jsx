import Card from "../common/Card.jsx";

const toneClasses = {
  safe: "border-emerald-400/25 bg-emerald-400/[0.04]",
  info: "border-cyan-400/25 bg-cyan-400/[0.04]",
  warning: "border-yellow-400/25 bg-yellow-400/[0.04]",
  danger: "border-red-400/25 bg-red-400/[0.04]",
};

function MetricsGrid({ metrics = [] }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <Card key={metric.label} className={`p-5 ${toneClasses[metric.tone] || metric.className || ""}`}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-slate-400">{metric.label}</p>
                <p className="mt-2 text-2xl font-bold text-white">{metric.value}</p>
              </div>
              {Icon && (
                <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/10 p-2 text-cyan-200">
                  <Icon size={20} />
                </div>
              )}
            </div>
            {metric.hint && <p className="mt-4 text-xs leading-5 text-slate-500">{metric.hint}</p>}
          </Card>
        );
      })}
    </section>
  );
}

export default MetricsGrid;
