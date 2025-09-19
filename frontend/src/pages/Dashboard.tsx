import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  fetchIncidents,
  fetchLatestNotifications,
  fetchNotificationSummary,
  fetchSlaMetrics,
  fetchThreatLevel,
} from "../api/api";
import type { Incident, SLAMetrics, ThreatLevel } from "../api/api";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import "./Dashboard.css";

type NotifSummary = { email: boolean; telegram: boolean; webhook: boolean };
type Tab = "analytics" | "schedule" | "kpi";

const Dashboard = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [latestNotifications, setLatestNotifications] = useState<any[]>([]);
  const [notifSummary, setNotifSummary] = useState<NotifSummary>({
    email: true,
    telegram: false,
    webhook: true,
  });
  const [sla, setSla] = useState<SLAMetrics | null>(null);
  const [threatLevel, setThreatLevel] = useState<ThreatLevel | null>(null);

  const [tab, setTab] = useState<Tab>("analytics");
  const [error, setError] = useState<string>("");

  const { t, i18n } = useTranslation();
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        setError("");
        const [inc, slaM, notifSum, latest, threat] = await Promise.all([
          fetchIncidents(),
          fetchSlaMetrics(),
          fetchNotificationSummary(),
          fetchLatestNotifications(),
          fetchThreatLevel(30),
        ]);
        setIncidents(inc || []);
        setSla(slaM || null);
        setNotifSummary(notifSum || { email: false, telegram: false, webhook: false });
        setLatestNotifications(latest || []);
        setThreatLevel(threat || null);
      } catch (e: any) {
        console.error("dashboard load error:", e);
        setError(t("common.loadError"));
      }
    };
    load();
  }, [i18n.language, t]);

  const greeting = useMemo(() => {
    const h = new Date().getHours();
    if (h < 5) return t("dashboard.goodNight");
    if (h < 12) return t("dashboard.goodMorning");
    if (h < 18) return t("dashboard.goodDay");
    return t("dashboard.goodEvening");
  }, [t]);

  const { openMonth, closedMonth, totalMonth } = useMemo(() => {
    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth();
    const inMonth = (d: Date) => d.getFullYear() === y && d.getMonth() === m;

    const open = incidents.filter(
      (i) => i.status === "open" && inMonth(new Date(i.created_at))
    ).length;

    const closed = incidents.filter(
      (i) => i.status !== "open" && inMonth(new Date(i.created_at))
    ).length;

    const total = incidents.filter((i) => inMonth(new Date(i.created_at))).length;

    return { openMonth: open, closedMonth: closed, totalMonth: total };
  }, [incidents]);

  const activeChannels =
    (notifSummary.email ? 1 : 0) +
    (notifSummary.telegram ? 1 : 0) +
    (notifSummary.webhook ? 1 : 0);

  const toggleChannel = (name: keyof NotifSummary) =>
    setNotifSummary((p) => ({ ...p, [name]: !p[name] }));

  return (
    <div className="dashboard-bg py-4">
      {/* header + tabs */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body d-flex flex-wrap justify-content-between align-items-center gap-3">
          <div>
            <div className="text-muted small mb-1">{greeting}</div>
            <h3 className="m-0">{currentUser?.email ?? "SOC Client"}</h3>
          </div>

          <ul className="nav nav-pills">
            <li className="nav-item">
              <button
                type="button"
                className={`nav-link ${tab === "schedule" ? "active" : ""}`}
                onClick={() => setTab("schedule")}
              >
                {t("dashboard.tabs.schedule")}
              </button>
            </li>
            <li className="nav-item">
              <button
                type="button"
                className={`nav-link ${tab === "analytics" ? "active" : ""}`}
                onClick={() => setTab("analytics")}
              >
                {t("dashboard.tabs.analytics")}
              </button>
            </li>
            <li className="nav-item">
              <button
                type="button"
                className={`nav-link ${tab === "kpi" ? "active" : ""}`}
                onClick={() => setTab("kpi")}
              >
                {t("dashboard.tabs.sla")}
              </button>
            </li>
            <li className="nav-item">
              <button
                type="button"
                className="nav-link"
                onClick={() => navigate("/tickets")}
              >
                {t("navigation.tickets")}
              </button>
            </li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {t("common.error")}: {error}
        </div>
      )}

      {/* THREAT LEVEL */}
      {threatLevel && (
        <div className="row mb-4">
          <div className="col-12">
            <div className={`card border-0 shadow-sm border-${threatLevel.color}`}>
              <div className="card-body">
                <div className="row align-items-center">
                  <div className="col-md-8">
                    <h5 className="card-title mb-2">
                      {t("dashboard.threat.title")}{" "}
                      <span className={`text-${threatLevel.color} fw-bold`}>
                        {threatLevel.threat_level.toUpperCase()}
                      </span>
                    </h5>
                    <div className="row text-center">
                      <div className="col">
                        <div className="text-muted small">{t("dashboard.threat.total")}</div>
                        <div className="h5 m-0">{threatLevel.total_incidents}</div>
                      </div>
                      <div className="col">
                        <div className="text-muted small">{t("dashboard.threat.high")}</div>
                        <div className="h5 m-0 text-danger">{threatLevel.high_priority}</div>
                      </div>
                      <div className="col">
                        <div className="text-muted small">{t("dashboard.threat.open")}</div>
                        <div className="h5 m-0 text-warning">{threatLevel.open_incidents}</div>
                      </div>
                      <div className="col">
                        <div className="text-muted small">{t("dashboard.threat.trend")}</div>
                        <div className="h5 m-0">
                          {threatLevel.trend === "increasing" && "↗️"}
                          {threatLevel.trend === "decreasing" && "↘️"}
                          {threatLevel.trend === "stable" && "→"}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-4 text-center">
                    <div className="display-4 fw-bold text-muted">{threatLevel.threat_score}</div>
                    <div className="text-muted">{t("dashboard.threat.of100")}</div>
                    <div className="progress mt-2">
                      <div
                        className={`progress-bar bg-${threatLevel.color}`}
                        style={{ width: `${threatLevel.threat_score}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* KPI TAB (SLA + Channels small card) */}
      {tab === "kpi" && (
        <div className="row g-3">
          <div className="col-lg-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">{t("dashboard.sla.title")}</h5>
                <div className="row text-center">
                  <div className="col">
                    <div className="text-muted small">{t("dashboard.sla.avgResponse")}</div>
                    <div className="h4 m-0">{sla?.avg_response_minutes ?? "0"}m</div>
                  </div>
                  <div className="col">
                    <div className="text-muted small">{t("dashboard.sla.avgResolution")}</div>
                    <div className="h4 m-0">{sla?.avg_resolution_minutes ?? "0"}m</div>
                  </div>
                </div>
                <hr />
                <div className="text-muted small mb-2">{t("dashboard.sla.compliance")}</div>
                <div className="progress">
                  <div className="progress-bar" style={{ width: "45%" }} />
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">{t("dashboard.activeChannels.title")}</h5>
                <p className="display-6 m-0">{activeChannels}/3</p>
                <p className="text-muted mb-0">{t("dashboard.activeChannels.switchOnAnalytics")}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ANALYTICS TAB */}
      {tab === "analytics" && (
        <>
          {/* KPI cards */}
          <div className="row g-3 mb-4">
            <div className="col-lg-3 col-md-6">
              <div className="card h-100 border-0 shadow-sm position-relative">
                <div className="card-body">
                  <div className="text-muted small">{t("dashboard.cards.openIncidents")}</div>
                  <div className="h4 m-0">{openMonth}</div>
                  <div className="small text-muted">{t("dashboard.thisMonth")}</div>
                </div>
                <Link to="/incidents?status=open" className="stretched-link" aria-label={t("dashboard.cards.openIncidents")} />
              </div>
            </div>

            <div className="col-lg-3 col-md-6">
              <div className="card h-100 border-0 shadow-sm position-relative">
                <div className="card-body">
                  <div className="text-muted small">{t("dashboard.cards.closedIncidents")}</div>
                  <div className="h4 m-0">{closedMonth}</div>
                  <div className="small text-muted">{t("dashboard.thisMonth")}</div>
                </div>
                <Link to="/incidents?status=closed" className="stretched-link" aria-label={t("dashboard.cards.closedIncidents")} />
              </div>
            </div>

            <div className="col-lg-3 col-md-6">
              <div className="card h-100 border-0 shadow-sm position-relative">
                <div className="card-body">
                  <div className="text-muted small">{t("dashboard.cards.allIncidents")}</div>
                  <div className="h4 m-0">{totalMonth}</div>
                  <div className="small text-muted">{t("dashboard.thisMonth")}</div>
                </div>
                <Link to="/incidents" className="stretched-link" />
              </div>
            </div>

            <div className="col-lg-3 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body">
                  <div className="text-muted small">{t("dashboard.cards.activeChannels")}</div>
                  <div className="h4 m-0">{activeChannels}/3</div>
                  <div className="small text-muted">{t("dashboard.current")}</div>
                </div>
              </div>
            </div>
          </div>

          {/* SLA + channels */}
          <div className="row g-3 mb-4">
            <div className="col-lg-8">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body">
                  <div className="mb-2 text-muted small">{t("dashboard.sla.snapshot")}</div>
                  <h5 className="card-title mb-3">{t("dashboard.sla.responseAndResolution")}</h5>
                  <div className="row text-center mb-3">
                    <div className="col">
                      <div className="text-muted small">{t("dashboard.sla.avgResponse")}</div>
                      <div className="h4 m-0">{sla?.avg_response_minutes ?? "0"}m</div>
                    </div>
                    <div className="col">
                      <div className="text-muted small">{t("dashboard.sla.avgResolution")}</div>
                      <div className="h4 m-0">{sla?.avg_resolution_minutes ?? "0"}m</div>
                    </div>
                  </div>

                  <div className="text-muted small mb-2">{t("dashboard.sla.compliance")}</div>
                  <div className="progress" role="progressbar">
                    <div className="progress-bar" style={{ width: "45%" }} />
                  </div>
                </div>
              </div>
            </div>

            <div className="col-lg-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body">
                  <h5 className="card-title">{t("dashboard.notificationChannels")}</h5>

                  <div className="d-flex justify-content-between align-items-center py-2">
                    <div className="d-flex align-items-center gap-2">
                      <i className="bi bi-envelope-fill text-primary" />
                      <span>Email</span>
                    </div>
                    <div className="form-check form-switch m-0">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        checked={notifSummary.email}
                        onChange={() => toggleChannel("email")}
                      />
                    </div>
                  </div>

                  <div className="d-flex justify-content-between align-items-center py-2">
                    <div className="d-flex align-items-center gap-2">
                      <i className="bi bi-telegram text-info" />
                      <span>Telegram</span>
                    </div>
                    <div className="form-check form-switch m-0">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        checked={notifSummary.telegram}
                        onChange={() => toggleChannel("telegram")}
                      />
                    </div>
                  </div>

                  <div className="d-flex justify-content-between align-items-center py-2">
                    <div className="d-flex align-items-center gap-2">
                      <i className="bi bi-link-45deg text-secondary" />
                      <span>Webhook</span>
                    </div>
                    <div className="form-check form-switch m-0">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        checked={notifSummary.webhook}
                        onChange={() => toggleChannel("webhook")}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent incidents + tickets + latest notifications */}
          <div className="row g-3">
            <div className="col-lg-8">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h5 className="card-title mb-0">{t("dashboard.recentIncidents")}</h5>
                    <div className="btn-group">
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => navigate("/incidents?status=open")}
                      >
                        {t("dashboard.open")}
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => navigate("/incidents?status=closed")}
                      >
                        {t("dashboard.closed")}
                      </button>
                    </div>
                  </div>

                  <div className="table-responsive">
                    <table className="table table-hover align-middle">
                      <thead className="table-light">
                        <tr>
                          <th style={{ width: 80 }}>ID</th>
                          <th>{t("dashboard.title")}</th>
                          <th style={{ width: 120 }}>{t("dashboard.status")}</th>
                          <th style={{ width: 180 }}>{t("dashboard.created")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {incidents.slice(0, 6).map((row) => (
                          <tr
                            key={row.id}
                            role="button"
                            onClick={() => navigate(`/incidents/${row.id}`)}
                          >
                            <td>#{row.id}</td>
                            <td>{row.title}</td>
                            <td>
                              <span
                                className={`badge ${
                                  row.status === "open"
                                    ? "text-bg-warning"
                                    : "text-bg-success"
                                }`}
                              >
                                {row.status}
                              </span>
                            </td>
                            <td>{new Date(row.created_at).toLocaleString()}</td>
                          </tr>
                        ))}
                        {incidents.length === 0 && (
                          <tr>
                            <td colSpan={4} className="text-center text-muted py-4">
                              {t("common.noData")}
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-lg-4 d-flex flex-column gap-3">
              <div className="card border-0 shadow-sm">
                <div className="card-body">
                  <h5 className="card-title">{t("dashboard.supportTickets")}</h5>
                  <button
                    className="btn btn-primary w-100 mb-2"
                    onClick={() => navigate("/tickets")}
                    type="button"
                  >
                    {t("dashboard.viewTickets")}
                  </button>
                  <button
                    className="btn btn-outline-primary w-100"
                    onClick={() => navigate("/tickets/new")}
                    type="button"
                  >
                    {t("dashboard.createNewTicket")}
                  </button>
                </div>
              </div>

              <div className="card border-0 shadow-sm">
                <div className="card-body">
                  <h5 className="card-title">{t("dashboard.latestNotifications")}</h5>
                  {latestNotifications.length === 0 ? (
                    <div className="text-muted">{t("common.noNotifications")}</div>
                  ) : (
                    <ul className="list-group list-group-flush">
                      {latestNotifications.slice(0, 5).map((n: any, i: number) => (
                        <li key={i} className="list-group-item px-0">
                          <div className="small text-muted">
                            {new Date(n.created_at).toLocaleString()}
                          </div>
                          <div>{n.title || n.message}</div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* SCHEDULE TAB (заглушка) */}
      {tab === "schedule" && (
        <div className="row g-3">
          <div className="col-lg-7">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">{t("dashboard.upcoming")}</h5>
                <p className="text-muted m-0">
                  {t("dashboard.calendarStub")}
                </p>
              </div>
            </div>
          </div>
          <div className="col-lg-5">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">{t("dashboard.quickActions")}</h5>
                <div className="d-grid gap-2">
                  <button
                    className="btn btn-primary"
                    onClick={() => navigate("/incidents")}
                  >
                    {t("dashboard.gotoIncidents")}
                  </button>
                  <button
                    className="btn btn-outline-primary"
                    onClick={() => navigate("/tickets/new")}
                  >
                    {t("dashboard.createNewTicket")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
