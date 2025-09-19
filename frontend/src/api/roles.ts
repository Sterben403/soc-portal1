// src/api/roles.ts
import axios from "./http"; // твой настроенный axios с baseURL и токеном

export async function requestRole(role: "analyst" | "manager") {
  const { data } = await axios.post("/api/roles/request", { role });
  return data;
}

export async function listRoleRequests(status: "pending" | "approved" | "rejected" = "pending") {
  const { data } = await axios.get("/api/roles/requests", { params: { status } });
  return data;
}

export async function approveRoleRequest(id: number) {
  const { data } = await axios.post(`/api/roles/requests/${id}/approve`);
  return data;
}

export async function rejectRoleRequest(id: number, comment?: string) {
  const { data } = await axios.post(`/api/roles/requests/${id}/reject`, { comment });
  return data;
}

export async function getPendingCount(): Promise<number> {
  const { data } = await axios.get("/api/roles/requests/count", { params: { status: "pending" } });
  return data?.count ?? 0;
}
