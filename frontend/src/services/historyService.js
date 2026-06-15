import api, { unwrapData } from "./api";

export async function getHistory(page = 1, pageSize = 10) {
  const response = await api.get("/history", {
    params: {
      page,
      page_size: pageSize,
    },
  });

  return unwrapData(response);
}

export async function getHistoryDetail(analysisId) {
  if (!analysisId) {
    throw new Error("analysisId is required.");
  }

  const response = await api.get(`/history/${analysisId}`);
  return unwrapData(response);
}

export default {
  getHistory,
  getHistoryDetail,
};
