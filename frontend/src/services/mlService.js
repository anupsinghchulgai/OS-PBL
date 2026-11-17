import { api, unwrap } from "./api";

export async function trainModel(payload) { return unwrap((await api.post("/ml/train", payload)).data); }
export async function trainingStatus(jobId) { return unwrap((await api.get(`/ml/train/${jobId}/status`)).data); }
export async function models() { return unwrap((await api.get("/ml/models")).data); }
export async function evaluate(payload) { return unwrap((await api.post("/ml/evaluate", payload)).data); }
export async function recommend(payload) { return unwrap((await api.post("/ml/recommend", payload)).data); }
export async function history() { return unwrap((await api.get("/ml/training-history")).data); }
export async function featureImportance() { return unwrap((await api.get("/ml/feature-importance")).data); }
