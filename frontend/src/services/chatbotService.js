import api, { unwrapData } from "./api";

export async function explainAnalysis(payload) {
  if (!payload) {
    throw new Error("Analysis payload is required.");
  }

  const response = await api.post("/chatbot/explain", payload);
  return unwrapData(response);
}

export async function getSuggestedQuestions() {
  const response = await api.get("/chatbot/suggestions");
  return unwrapData(response);
}

export default {
  explainAnalysis,
  getSuggestedQuestions,
};
