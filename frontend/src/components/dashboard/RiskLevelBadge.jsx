import Badge from "../common/Badge.jsx";

function normalizeRisk(level = "") {
  const value = String(level).toLowerCase();
  if (value.includes("high") || value.includes("critical")) return { tone: "danger", label: level || "High Risk" };
  if (value.includes("medium") || value.includes("moderate")) return { tone: "warning", label: level || "Medium Risk" };
  if (value.includes("low")) return { tone: "success", label: level || "Low Risk" };
  return { tone: "info", label: level || "Unknown Risk" };
}

function RiskLevelBadge({ level, className = "" }) {
  const risk = normalizeRisk(level);
  return (
    <Badge tone={risk.tone} className={className}>
      {risk.label}
    </Badge>
  );
}

export default RiskLevelBadge;
