import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Alert,
  Badge,
  Button,
  ButtonGroup,
  Form,
  Modal,
  Spinner,
  ToggleButton,
} from "react-bootstrap";
import { useAuth } from "../context/AuthContext";
import { fetchIncidents, type Incident, createIncident } from "../api/api";
import { useTranslation } from "react-i18next";

type Tab = "all" | "open" | "closed";

export default function Incidents() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { t } = useTranslation();

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [q, setQ] = useState("");
  const [tab, setTab] = useState<Tab>(() => {
    const t0 = (params.get("status") || "all").toLowerCase();
    return (["all", "open", "closed"].includes(t0) ? t0 : "all") as Tab;
  });

  // --- создание инцидента (для analyst/manager/admin) ---
  const canCreate = ["analyst", "manager", "admin"].includes(
    (currentUser?.role || "").toLowerCase()
  );
  const [showNewModal, setShowNewModal] = useState(false);
  const [formTitle, setFormTitle] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formPriority, setFormPriority] = useState<"low" | "medium" | "high">("medium");
  const [creating, setCreating] = useState(false);

  const doCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formTitle.trim()) return;
    setCreating(true);
    try {
      await createIncident({
        title: formTitle.trim(),
        description: formDescription.trim(),
        priority: formPriority,
      });
      setShowNewModal(false);
      setFormTitle("");
      setFormDescription("");
      setFormPriority("medium");
      await load();
    } catch (e: any) {
      setError(e?.message || t("common.error"));
    } finally {
      setCreating(false);
    }
  };

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchIncidents();
      setIncidents(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e?.message || (t("common.loadError") as string));
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = useMemo(() => {
    let rows = incidents;
    if (tab !== "all") rows = rows.filter((i) => i.status === tab);
    if (q.trim()) {
      const s = q.trim().toLowerCase();
      rows = rows.filter(
        (i) =>
          i.title.toLowerCase().includes(s) ||
          (i.description || "").toLowerCase().includes(s)
      );
    }
    return rows;
  }, [incidents, tab, q]);

  return (
    <div className="container mt-4">
      <h3 className="mb-3">{t("incidents.title")}</h3>

      <div className="d-flex flex-wrap gap-2 align-items-center mb-3">
        <ButtonGroup>
          <ToggleButton
            id="tab-all"
            type="radio"
            variant={tab === "all" ? "primary" : "outline-primary"}
            checked={tab === "all"}
            value="all"
            onClick={() => setTab("all")}
          >
            {t("incidents.tabs.all")}
          </ToggleButton>
          <ToggleButton
            id="tab-open"
            type="radio"
            variant={tab === "open" ? "primary" : "outline-primary"}
            checked={tab === "open"}
            value="open"
            onClick={() => setTab("open")}
          >
            {t("incidents.tabs.open")}
          </ToggleButton>
          <ToggleButton
            id="tab-closed"
            type="radio"
            variant={tab === "closed" ? "primary" : "outline-primary"}
            checked={tab === "closed"}
            value="closed"
            onClick={() => setTab("closed")}
          >
            {t("incidents.tabs.closed")}
          </ToggleButton>
        </ButtonGroup>

        <Form.Control
          placeholder={(t("incidents.searchPlaceholder") as string) || "Search…"}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ maxWidth: 420 }}
        />

        <Button variant="outline-secondary" onClick={load}>
          {t("common.refresh")}
        </Button>

        {canCreate && (
          <Button onClick={() => setShowNewModal(true)}>
            {t("incidents.new", { defaultValue: "New incident" })}
          </Button>
        )}
      </div>

      {error && <Alert variant="danger">HTTP: {error}</Alert>}

      {loading ? (
        <div className="text-center my-5">
          <Spinner animation="border" />
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead className="table-light">
              <tr>
                <th style={{ width: 90 }}>ID</th>
                <th>{t("incidents.col.title")}</th>
                <th style={{ width: 140 }}>{t("incidents.col.status")}</th>
                <th style={{ width: 220 }}>{t("incidents.col.created")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr
                  key={row.id}
                  role="button"
                  onClick={() => navigate(`/incidents/${row.id}`)}
                >
                  <td>#{row.id}</td>
                  <td>{row.title}</td>
                  <td>
                    <Badge bg={row.status === "open" ? "warning" : "success"}>
                      {row.status}
                    </Badge>
                  </td>
                  <td>{new Date(row.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center text-muted py-4">
                    {t("common.nothingFound")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="text-muted small mt-2">
        {t("incidents.currentRole")}:{" "}
        <strong>{t(`roles.${currentUser?.role ?? "client"}`)}</strong>
      </div>

      {/* Modal: создание инцидента */}
      <Modal show={showNewModal} onHide={() => setShowNewModal(false)} centered>
        <Form onSubmit={doCreate}>
          <Modal.Header closeButton>
            <Modal.Title>
              {t("incidents.new", { defaultValue: "New incident" })}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>{t("incidents.col.title")}</Form.Label>
              <Form.Control
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
                required
                placeholder={t("incidents.col.title") as string}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>
                {t("incident.fields.description", { defaultValue: "Description" })}
              </Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
              />
            </Form.Group>
            <Form.Group>
              <Form.Label>
                {t("incident.fields.priority", { defaultValue: "Priority" })}
              </Form.Label>
              <Form.Select
                value={formPriority}
                onChange={(e) => setFormPriority(e.target.value as any)}
              >
                <option value="low">{t("priority.low", { defaultValue: "Low" })}</option>
                <option value="medium">
                  {t("priority.medium", { defaultValue: "Medium" })}
                </option>
                <option value="high">{t("priority.high", { defaultValue: "High" })}</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="light" onClick={() => setShowNewModal(false)}>
              {t("common.cancel")}
            </Button>
            <Button type="submit" disabled={creating}>
              {creating ? t("common.loading") : t("common.create")}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
}
