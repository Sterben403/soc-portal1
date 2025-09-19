// src/pages/IncidentDetails.tsx
import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Alert,
  Badge,
  Button,
  Card,
  Form,
  ListGroup,
  Spinner,
  Tabs,
  Tab,
} from "react-bootstrap";
import api from "../api/http";
import { type Incident, getMessages, sendMessage } from "../api/api";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";

type HistoryItem = {
  id: number;
  user_id: number;
  action: string;
  details?: string | null;
  created_at: string;
};

type ChatMessage = {
  id: number;
  message: string;
  sender_role: string;
  created_at: string;
  attachment_id?: number;
  file_name?: string;
};

type IncidentWithOptional = Incident & {
  priority?: string;
  first_response_at?: string | null;
  closed_at?: string | null;
};

export default function IncidentDetails() {
  const { id } = useParams<{ id: string }>();
  const incidentId = useMemo(() => Number(id), [id]);
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const { t } = useTranslation();

  const [incident, setIncident] = useState<IncidentWithOptional | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>(""); // <-- имя выбранного файла (для показа)
  const [tab, setTab] = useState<string>("overview");

  const isManager = (currentUser?.role || "").toLowerCase() === "manager";

  // -------- loaders ----------
  const loadIncident = async () => {
    setError("");
    try {
      const { data } = await api.get<IncidentWithOptional>(`/api/incidents/${incidentId}`);
      setIncident(data);
    } catch (e: any) {
      setError(e?.message ?? (t("common.loadError") as string));
    }
  };

  const loadHistory = async () => {
    try {
      const { data } = await api.get<HistoryItem[]>(`/api/incidents/${incidentId}/history`);
      setHistory(Array.isArray(data) ? data : []);
    } catch {
      /* ignore */
    }
  };

  const loadChatMessages = async () => {
    try {
      const data = (await getMessages(incidentId)) as ChatMessage[];
      setMessages(Array.isArray(data) ? data : []);
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    if (!incidentId) return;
    (async () => {
      setLoading(true);
      await Promise.all([loadIncident(), loadHistory(), loadChatMessages()]);
      setLoading(false);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  // -------- actions ----------
  const refetchAfterAction = async () => {
    await Promise.all([loadIncident(), loadHistory()]);
  };

  const postAction = async (path: "close" | "confirm" | "reopen") => {
    try {
      await api.post(`/api/incidents/${incidentId}/${path}`);
      await refetchAfterAction();
    } catch (e: any) {
      setError(e?.message ?? (t("common.error") as string));
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() && !file) return;
    try {
      const form = new FormData();
      form.append("incident_id", String(incidentId));
      if (newMessage.trim()) form.append("message", newMessage.trim());
      if (file) form.append("file", file);

      await sendMessage(incidentId, form);
      setNewMessage("");
      setFile(null);
      setFileName("");
      await loadChatMessages();
    } catch (e: any) {
      setError(e?.message ?? (t("incidents.chat.sendError") as string));
    }
  };

  // -------- UI ----------
  if (loading && !incident) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" />
      </div>
    );
  }
  if (!incident) {
    return <Alert variant="danger">{t("incident.notFound")}</Alert>;
  }

  return (
    <div className="container mt-4">
      {error && (
        <Alert variant="danger" onClose={() => setError("")} dismissible>
          {error}
        </Alert>
      )}

      <Button variant="outline-secondary" className="mb-3" onClick={() => navigate(-1)}>
        ← {t("common.back") || "Back"}
      </Button>

      <Card className="mb-3 shadow-sm border-0">
        <Card.Body className="d-flex flex-wrap justify-content-between align-items-start gap-3">
          <div>
            <h4 className="mb-1">{incident.title}</h4>
            <div className="text-muted small">
              #{incident.id} · {t("incident.createdAt", { defaultValue: "created" })}{" "}
              {new Date(incident.created_at).toLocaleString()}
            </div>
          </div>
          <div className="d-flex align-items-center gap-2">
            <Badge bg={incident.status === "open" ? "warning" : "success"}>
              {incident.status}
            </Badge>

            <div className="btn-group">
              <Button
                size="sm"
                variant="outline-primary"
                disabled={isManager}
                onClick={() => postAction("close")}
              >
                {t("incident.buttons.close")}
              </Button>
              <Button
                size="sm"
                variant="outline-success"
                disabled={isManager}
                onClick={() => postAction("confirm")}
              >
                {t("incident.buttons.confirm")}
              </Button>
              <Button
                size="sm"
                variant="outline-secondary"
                disabled={isManager}
                onClick={() => postAction("reopen")}
              >
                {t("incident.buttons.reopen")}
              </Button>
            </div>
          </div>
        </Card.Body>
      </Card>

      <Tabs activeKey={tab} onSelect={(k) => setTab(k ?? "overview")} className="mb-3">
        {/* ОПИСАНИЕ */}
        <Tab eventKey="overview" title={t("incident.tabs.overview")}>
          <Card className="border-0 shadow-sm">
            <Card.Body>
              <h6 className="text-muted mb-2">{t("incident.tabs.overview")}</h6>
              <div className="mb-3">{incident.description || "—"}</div>

              <div className="row g-3 small text-muted">
                <div className="col-md-4">
                  <div className="fw-semibold text-dark">{t("incident.fields.status")}</div>
                  <span
                    className={`badge ${
                      incident.status === "open" ? "text-bg-warning" : "text-bg-success"
                    }`}
                  >
                    {incident.status}
                  </span>
                </div>
                <div className="col-md-4">
                  <div className="fw-semibold text-dark">{t("incident.fields.priority")}</div>
                  <span className="badge text-bg-secondary">{incident.priority || "—"}</span>
                </div>
                <div className="col-md-4">
                  <div className="fw-semibold text-dark">{t("incident.fields.created")}</div>
                  {new Date(incident.created_at).toLocaleString()}
                </div>
              </div>
            </Card.Body>
          </Card>
        </Tab>

        {/* ХРОНОЛОГИЯ */}
        <Tab eventKey="history" title={t("incident.tabs.history")}>
          <Card className="border-0 shadow-sm">
            <Card.Body>
              {history.length === 0 ? (
                <div className="text-muted">{t("incident.noEvents")}</div>
              ) : (
                <ListGroup variant="flush">
                  {history.map((h) => (
                    <ListGroup.Item key={h.id} className="px-0">
                      <div className="d-flex justify-content-between">
                        <div className="fw-semibold">
                          {/* локализуем действие */}
                          {t(`incident.history.actions.${h.action}`, h.action)}
                          <span className="text-muted ms-2">· user #{h.user_id}</span>
                        </div>
                        <small className="text-muted">
                          {new Date(h.created_at).toLocaleString()}
                        </small>
                      </div>
                      {!!h.details && (
                        <div className="text-muted small mt-1">{h.details}</div>
                      )}
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Card.Body>
          </Card>
        </Tab>

        {/* ОБСУЖДЕНИЕ */}
        <Tab eventKey="chat" title={t("incident.tabs.chat")}>
          <Card className="border-0 shadow-sm">
            <Card.Body>
              {messages.length === 0 ? (
                <div className="text-muted mb-3">{t("incidents.chat.empty")}</div>
              ) : (
                <ListGroup className="mb-3" variant="flush">
                  {messages.map((m) => (
                    <ListGroup.Item key={m.id} className="px-0">
                      <div className="d-flex justify-content-between mb-1">
                        <strong>
                          {m.sender_role === "client" ? t("roles.client") : m.sender_role}
                        </strong>
                        <small className="text-muted">
                          {new Date(m.created_at).toLocaleString()}
                        </small>
                      </div>
                      <div>{m.message}</div>
                      {m.attachment_id && (
                        <div className="mt-1">
                          <a
                            href={`/attachments/${m.attachment_id}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            ⬇{" "}
                            {t("incident.downloadAttachment", {
                              defaultValue: "Download attachment",
                            })}{" "}
                            {m.file_name || ""}
                          </a>
                        </div>
                      )}
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}

              <Form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
              >
                <Form.Group className="mb-2">
                  <Form.Control
                    as="textarea"
                    rows={3}
                    placeholder={
                      isManager
                        ? (t("incident.chat.placeholderManager") as string)
                        : (t("incidents.chat.placeholder") as string)
                    }
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    disabled={isManager}
                  />
                </Form.Group>

                {/* Скрытый file input + кастомная кнопка */}
                <input
                  id="incident-chat-file"
                  type="file"
                  className="d-none"
                  onChange={(e: ChangeEvent<HTMLInputElement>) => {
                    const f = e.currentTarget.files?.[0] ?? null;
                    setFile(f);
                    setFileName(f ? f.name : "");
                  }}
                  disabled={isManager}
                />

                <div className="d-flex align-items-center gap-3">
                  <Button
                    type="button"
                    variant="outline-secondary"
                    onClick={() => document.getElementById("incident-chat-file")?.click()}
                    disabled={isManager}
                  >
                    {t("incidents.chat.attach")}
                  </Button>

                  <span className="text-muted small">
                    {fileName || t("incidents.chat.noFile")}
                  </span>

                  <Button
                    type="submit"
                    className="ms-auto"
                    disabled={isManager || (!newMessage.trim() && !file)}
                  >
                    {t("common.send")}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
}
