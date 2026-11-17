import { api, unwrap } from "./api";

export async function health() { return unwrap((await api.get("/health")).data); }
export async function simulate(payload) { return unwrap((await api.post("/simulate", payload)).data); }
export async function compare(payload) { return unwrap((await api.post("/compare", payload)).data); }
export async function generateProcesses(payload) { return unwrap((await api.post("/generate-processes", payload)).data); }

export function normalizeSimulation(raw) {
  const data = raw?.simulation || raw?.result || raw;
  const timeline = data?.timeline || data?.gantt || data?.execution_timeline || data?.segments || [];
  const metrics = data?.metrics || data?.summary || {};
  const processes = data?.processes || data?.process_metrics || data?.process_results || [];
  return { ...data, timeline, metrics, processes };
}
