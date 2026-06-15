import api, { API_BASE_URL, unwrapData } from "./api";

export async function getReports() {
  const response = await api.get("/reports");
  return unwrapData(response);
}

export async function getReportText(reportId) {
  if (!reportId) {
    throw new Error("reportId is required.");
  }

  const response = await api.get(`/reports/${reportId}`, {
    responseType: "text",
  });

  return response.data;
}

export function getReportDownloadUrl(reportId) {
  if (!reportId) {
    return "";
  }

  return `${API_BASE_URL}/api/reports/${reportId}/download`;
}

export async function downloadReport(reportId) {
  if (!reportId) {
    throw new Error("reportId is required.");
  }

  const response = await api.get(`/reports/${reportId}/download`, {
    responseType: "blob",
  });

  return response.data;
}

export default {
  getReports,
  getReportText,
  getReportDownloadUrl,
  downloadReport,
};
