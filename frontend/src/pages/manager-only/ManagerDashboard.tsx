import { useEffect, useState } from "react";
import { Alert, Card, ListGroup, Spinner, Badge, Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

type Incident = { id: number; title: string; status: string; created_at: string; };
type ReportItem = { id: number; name: string; created_at: string; };

const BASE_URL = "";

export default function ManagerDashboard() {
  const { t } = useTranslation();
  const [inc, setInc] = useState<Incident[]>([]);
  const [archive, setArchive] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const load = async () => {
    setLoading(true); setError("");
    try {
      const [iRes, aRes] = await Promise.all([
        fetch(`${BASE_URL}/api/incidents/my`, { credentials: "include" }),
        fetch(`${BASE_URL}/report/report/archive`, { credentials: "include" }),
      ]);
      if (!iRes.ok) throw new Error(`incidents: ${iRes.status}`);
      if (!aRes.ok) throw new Error(`archive: ${aRes.status}`);
      const iData = (await iRes.json()) as Incident[];
      const aData = (await aRes.json()) as ReportItem[];
      setInc(Array.isArray(iData) ? iData.slice(0, 8) : []);
      setArchive(Array.isArray(aData) ? aData.slice(0, 8) : []);
    } catch (e: any) {
      setError(e?.message || t("common.loadError"));
      setInc([]); setArchive([]);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const download = async (reportId: number) => {
    const res = await fetch(`${BASE_URL}/report/report/archive/${reportId}`, { credentials: "include" });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `report_${reportId}.zip`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mt-4">
      <h3 className="mb-3">{t("manager.title")}</h3>

      {error && <Alert variant="danger">{t("common.error")}: {error}</Alert>}

      {loading ? (
        <div className="text-center my-5"><Spinner animation="border" /></div>
      ) : (
        <div className="row g-3">
          <div className="col-lg-6">
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="fw-semibold">{t("manager.latestIncidents")}</Card.Header>
              <ListGroup variant="flush">
                {inc.length === 0 && <ListGroup.Item className="text-muted">{t("common.noData")}</ListGroup.Item>}
                {inc.map(i => (
                  <ListGroup.Item key={i.id}>
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <div className="fw-semibold">#{i.id} · {i.title}</div>
                        <div className="small text-muted">{new Date(i.created_at).toLocaleString()}</div>
                      </div>
                      <Badge bg={i.status === "open" ? "warning" : "success"}>{i.status}</Badge>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          </div>

          <div className="col-lg-6">
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="fw-semibold">{t("manager.reportsArchive")}</Card.Header>
              <ListGroup variant="flush">
                {archive.length === 0 && <ListGroup.Item className="text-muted">{t("manager.archiveEmpty")}</ListGroup.Item>}
                {archive.map(r => (
                  <ListGroup.Item key={r.id} className="d-flex justify-content-between align-items-center">
                    <div>
                      <div className="fw-semibold">{r.name || `${t("manager.report")} #${r.id}`}</div>
                      <div className="small text-muted">{new Date(r.created_at).toLocaleString()}</div>
                    </div>
                    <Button size="sm" variant="outline-primary" onClick={() => download(r.id)}>
                      {t("common.download")}
                    </Button>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card>
          </div>

          <div className="col-12">
            <Card className="border-0 shadow-sm">
              <Card.Body>
                <h5 className="mb-2">{t("manager.subscriptionTitle")}</h5>
                <p className="text-muted mb-2">{t("manager.subscriptionHint")}</p>
                <Button disabled variant="secondary">{t("common.soon")}</Button>
              </Card.Body>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
