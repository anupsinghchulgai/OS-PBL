import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000
});

export function unwrap(payload) {
  if (payload && typeof payload === "object") {
    if ("data" in payload && payload.data !== null) return payload.data;
    if ("result" in payload && payload.result !== null) return payload.result;
  }
  return payload;
}

export function apiError(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map(x => x.msg || JSON.stringify(x)).join(", ");
  if (typeof detail === "string") return detail;
  if (error?.response?.status) return `Request failed with HTTP ${error.response.status}.`;
  return error?.message || "Unable to reach the FastAPI backend.";
}
