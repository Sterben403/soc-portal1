import { useEffect, useState } from "react";
import { Alert, Card, ListGroup, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";

type Incident = { id: number; title: string; status: string; created_at: string; };
type Notification = { id?: number; title?: string; message?: string; created_at: string; };

const BASE_URL = "";

export default function AnalystDashboard() {
  const { t } = useTranslation();
  const [inc, setInc] = useState<Incident[]>([]);
  const [notifs, setNotifs] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [iRes, nRes] = await Promise.all([
        fetch(`${BASE_URL}/api/incidents/my`, { credentials: "include" }),
        fetch(`${BASE_URL}/api/notifications`, { credentials: "include" }),
      ]);
      if (!iRes.ok) throw new Error(`incidents: ${iRes.status}`);
      if (!nRes.ok) throw new Error(`notifications: ${nRes.status}`);
      const iData = (await iRes.json()) as Incident[];
      const nData = (await nRes.json()) as Notification[];
      setInc(Array.isArray(iData) ? iData.slice(0, 10) : []);
      setNotifs(Array.isArray(nData) ? nData.slice(0, 10) : []);
    } catch (e: any) {
      setError(e?.message || t("common.loadError"));
      setInc([]); setNotifs([]);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="container mt-4">
      <h3 className="mb-3">{t("analyst.title")}</h3>

      {error && <Alert variant="danger">{t("common.error")}: {error}</Alert>}

      {loading ? (
        <div className="text-center my-5"><Spinner animation="border" /></div>
      ) : (
        <div className="row g-3">
          <div className="col-lg-6">
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="fw-semibold">{t("analyst.latestIncidents")}</Card.Header>
              <ListGroup variant="flush">
                {inc.length === 0 && (<ListGroup.Item className="text-muted">{t("common.noData")}</ListGroup.Item>)}
                {inc.map((i) => (
                  <ListGroup.Item key={i.id}>
                    <div className="d-flex justify-content-between">
                      <div>
                        <div className="fw-semibold">#{i.id} · {i.title}</div>
                        <div className="small text-muted">{new Date(i.created_at).toLocaleString()}</div>
                      </div>
                      <div className="text-capitalize">{i.status}</div>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          </div>

          <div className="col-lg-6">
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="fw-semibold">{t("analyst.latestNotifications")}</Card.Header>
              <ListGroup variant="flush">
                {notifs.length === 0 && (<ListGroup.Item className="text-muted">{t("common.noNotifications")}</ListGroup.Item>)}
                {notifs.map((n, idx) => (
                  <ListGroup.Item key={n.id ?? idx}>
                    <div className="small text-muted mb-1">{new Date(n.created_at).toLocaleString()}</div>
                    <div>{n.title || n.message || "—"}</div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
