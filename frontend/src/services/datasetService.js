import { api, unwrap } from "./api";

export async function createDataset(payload) { return unwrap((await api.post("/datasets", payload)).data); }
export async function createSyntheticDataset(payload) { return unwrap((await api.post("/datasets/synthetic", payload)).data); }
export async function listDatasets() { return unwrap((await api.get("/datasets")).data); }
export async function getDataset(id) { return unwrap((await api.get(`/datasets/${id}`)).data); }
export async function uploadDataset(file) {
  const form = new FormData();
  form.append("file", file);
  return unwrap((await api.post("/datasets/upload", form, { headers: { "Content-Type": "multipart/form-data" } })).data);
}
export async function addRecord(id, record) { return unwrap((await api.post(`/datasets/${id}/records`, record)).data); }
export async function updateRecord(id, recordId, record) { return unwrap((await api.put(`/datasets/${id}/records/${recordId}`, record)).data); }
export async function deleteRecord(id, recordId) { return unwrap((await api.delete(`/datasets/${id}/records/${recordId}`)).data); }
export async function deleteDataset(id) { return unwrap((await api.delete(`/datasets/${id}`)).data); }

export async function downloadDataset(id) {
  const response = await api.get(`/datasets/${id}/download`, { responseType: "blob" });
  return response.data;
}
