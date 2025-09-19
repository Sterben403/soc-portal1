import { useEffect, useState } from "react";
import { Alert, Button, ButtonGroup, Card, Form, Spinner, ToggleButton } from "react-bootstrap";
import { useAuth } from "../context/AuthContext";
import api from "../api/http";
import { useTranslation } from "react-i18next";

type Format = "pdf" | "csv" | "xlsx";
type ReportItem = { id: number; filename: string; format: Format; created_at: string; };

export default function Reports() {
  const { currentUser } = useAuth();
  const role = currentUser?.role;
  const { t } = useTranslation();

  const [format, setFormat] = useState<Format>("pdf");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [archive, setArchive] = useState<ReportItem[]>([]);
  const [range, setRange] = useState<{ start?: string; end?: string }>({});

  const isAnalyst = role === "analyst";
  const isManager = role === "manager";

  const loadArchive = async () => {
    setError("");
    try {
      const { data } = await api.get<ReportItem[]>("/report/report/archive");
      setArchive(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e?.message || t("reports.archiveError"));
      setArchive([]);
    }
  };
  useEffect(() => { loadArchive(); }, []);

  const generate = async () => {
    setLoading(true); setError("");
    try {
      const base =
        format === "pdf" ? "/report/report/pdf" :
        format === "csv" ? "/report/report/csv" :
        "/report/report/xlsx";

      const params: any = {};
      if (range.start) params.start_date = range.start;
      if (range.end) params.end_date = range.end;

      const { data } = await api.get(base, { responseType: "blob", params });
      const blob = data as Blob;
      const a = document.createElement("a");
      const link = URL.createObjectURL(blob);
      a.href = link; a.download = `report.${format}`; a.click();
      URL.revokeObjectURL(link);
      await loadArchive();
    } catch (e: any) {
      setError(e?.message || t("reports.generateError"));
    } finally { setLoading(false); }
  };

  const sendToEmail = async () => {
    setLoading(true); setError("");
    try {
      const params: any = { format };
      if (range.start) params.start_date = range.start;
      if (range.end) params.end_date = range.end;
      await api.post("/report/report/send", null, { params });
      await loadArchive();
    } catch (e: any) {
      setError(e?.message || t("reports.emailError"));
    } finally { setLoading(false); }
  };

  const downloadFromArchive = async (id: number, filename: string) => {
    try {
      const { data } = await api.get(`/report/report/archive/${id}`, { responseType: "blob" });
      const blob = data as Blob;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = filename || `report_${id}`; a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(`${t("reports.downloadError")} #${id}: ${e?.message || ""}`);
    }
  };

  return (
    <div className="container mt-4">
      <h3 className="mb-3">{t("reports.title")}</h3>

      {error && <Alert variant="danger">{t("common.error")}: {error}</Alert>}

      <div className="row g-3">
        <div className="col-lg-6">
          <Card className="border-0 shadow-sm h-100">
            <Card.Body>
              <h5 className="mb-3">{t("reports.createTitle")}</h5>

              {!isAnalyst && (
                <Alert variant="secondary" className="py-2">
                  {t("reports.readOnly")}
                </Alert>
              )}

              <div className="mb-2">
                <div className="text-muted small mb-1">{t("reports.format")}</div>
                <ButtonGroup>
                  <ToggleButton id="fmt-pdf" type="radio" variant={format === "pdf" ? "primary" : "outline-primary"} checked={format === "pdf"} value="pdf" onClick={() => setFormat("pdf")}>PDF</ToggleButton>
                  <ToggleButton id="fmt-csv" type="radio" variant={format === "csv" ? "primary" : "outline-primary"} checked={format === "csv"} value="csv" onClick={() => setFormat("csv")}>CSV</ToggleButton>
                  <ToggleButton id="fmt-xlsx" type="radio" variant={format === "xlsx" ? "primary" : "outline-primary"} checked={format === "xlsx"} value="xlsx" onClick={() => setFormat("xlsx")}>XLSX</ToggleButton>
                </ButtonGroup>
              </div>

              <div className="d-flex gap-2 mb-3">
                <Form.Control type="date" value={range.start || ""} onChange={(e) => setRange((p) => ({ ...p, start: e.target.value }))} />
                <Form.Control type="date" value={range.end || ""} onChange={(e) => setRange((p) => ({ ...p, end: e.target.value }))} />
              </div>

              <div className="d-flex gap-2">
                <Button disabled={!isAnalyst || loading} onClick={generate}>
                  {loading ? <Spinner size="sm" animation="border" /> : t("reports.generate")}
                </Button>
                <Button variant="outline-primary" disabled={!isAnalyst || loading} onClick={sendToEmail}>
                  {t("reports.sendEmail")}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </div>

        <div className="col-lg-6">
          <Card className="border-0 shadow-sm h-100">
            <Card.Body>
              <h5 className="mb-3">{t("reports.archiveTitle")}</h5>
              <div className="list-group">
                {archive.length === 0 && (
                  <div className="list-group-item text-muted">{t("reports.archiveEmpty")}</div>
                )}
                {archive.map((r) => (
                  <div key={r.id} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <div className="fw-semibold">{r.filename || `${t("reports.report")} #${r.id}`}</div>
                      <div className="small text-muted">{new Date(r.created_at).toLocaleString()}</div>
                    </div>
                    <Button size="sm" variant="outline-secondary" onClick={() => downloadFromArchive(r.id, r.filename)}>
                      {t("common.download")}
                    </Button>
                  </div>
                ))}
              </div>
              {isManager && (
                <div className="text-muted small mt-3">
                  {t("reports.managerNote")}
                </div>
              )}
            </Card.Body>
          </Card>
        </div>
      </div>
    </div>
  );
}
