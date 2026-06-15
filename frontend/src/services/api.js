import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 120000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Unexpected API error";

    return Promise.reject({
      ...error,
      message,
      status: error.response?.status,
      payload: error.response?.data,
    });
  },
);

export function unwrapData(response) {
  return response.data?.data ?? response.data;
}

export default api;
