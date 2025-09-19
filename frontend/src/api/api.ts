// frontend/src/api/api.ts
import api from "./http";

export interface Incident {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

/** ---------- Incidents ---------- */
export type IncidentPayload = {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  client_id?: number | null;
};

export async function fetchIncidents(): Promise<Incident[]> {
  const { data } = await api.get("/api/incidents/my");
  return data;
}

export async function createIncident(payload: IncidentPayload) {
  const { data } = await api.post("/api/incidents", payload);
  return data;
}

/** ---------- Notifications ---------- */
export async function fetchNotifications(params?: Record<string, any>) {
  const { data } = await api.get("/api/notifications", { params });
  return data;
}
export async function fetchLatestNotifications() {
  const { data } = await api.get("/api/notifications/latest");
  return data;
}
export async function fetchNotificationSummary(): Promise<{
  email: boolean;
  telegram: boolean;
  webhook: boolean;
}> {
  const { data } = await api.get("/api/notifications/summary");
  return data;
}

/** ---------- SLA ---------- */
export interface SLAMetrics {
  avg_response_minutes: number;
  avg_resolution_minutes: number;
  total_closed: number;
  total_open: number;
}
export async function fetchSlaMetrics(): Promise<SLAMetrics> {
  const { data } = await api.get("/api/slametrics");
  return data;
}

/** ---------- Threat Level ---------- */
export interface ThreatLevel {
  threat_score: number;
  threat_level: string;
  color: string;
  total_incidents: number;
  high_priority: number;
  open_incidents: number;
  period_days: number;
  trend: string;
  period_start: string;
  period_end: string;
}
export async function fetchThreatLevel(periodDays: number = 30): Promise<ThreatLevel> {
  const { data } = await api.get("/api/threat-level", { params: { period_days: periodDays } });
  return data;
}

/** ---------- Incident Statistics ---------- */
export interface IncidentStats {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_day: Record<string, number>;
  avg_response_time: number;
  avg_resolution_time: number;
}
export async function fetchIncidentStats(periodDays: number = 30): Promise<IncidentStats> {
  const { data } = await api.get("/api/incident-stats", { params: { period_days: periodDays } });
  return data;
}

/** ---------- Reports ---------- */
export async function fetchReports(params?: {
  start_date?: string;
  end_date?: string;
  format?: "pdf" | "csv" | "xlsx";
}) {
  const { data } = await api.get("/report", { params });
  return data;
}

/** ---------- Tickets ---------- */
export async function fetchTickets(params?: Record<string, any>) {
  const { data } = await api.get("/api/tickets", { params });
  return data;
}
export async function createTicket(data: { category: string; title: string; message: string }) {
  const { data: resp } = await api.post("/api/tickets", data);
  return resp;
}
export async function fetchTicketMessages(ticketId: number) {
  const { data } = await api.get(`/api/tickets/${ticketId}/messages`);
  return data;
}
export async function replyToTicket(ticketId: number, message: string) {
  const { data } = await api.post(`/api/tickets/${ticketId}/reply`, { message });
  return data;
}

/** ---------- Incident messages ---------- */
export async function getMessages(incidentId: number) {
  const { data } = await api.get(`/api/messages/${incidentId}`);
  return data;
}
export async function sendMessage(_incidentId: number, formData: FormData) {
  const { data } = await api.post("/api/messages", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
