import api, { unwrapData } from "./api";

export async function analyzeFile(file, onUploadProgress) {
  if (!file) {
    throw new Error("Please choose a file before analysis.");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/analysis", formData, {
    timeout: 300000,
    onUploadProgress,
  });

  return unwrapData(response);
}

export default {
  analyzeFile,
};
