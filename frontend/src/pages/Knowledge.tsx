import { useEffect, useMemo, useState } from "react";
import { Button, Card, Form, Modal, Spinner, Alert } from "react-bootstrap";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";

type Article = {
  id: number;
  title: string;
  content: string;
  created_at?: string;
};

const BASE_URL = "";

export default function Knowledge() {
  const { currentUser } = useAuth();
  const role = currentUser?.role;
  const canEdit = useMemo(() => role === "analyst", [role]);
  const { t, i18n } = useTranslation();

  const [items, setItems] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string>("");

  // modal state
  const [show, setShow] = useState(false);
  const [editing, setEditing] = useState<Article | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const resetForm = () => {
    setEditing(null);
    setTitle("");
    setContent("");
  };

  const openCreate = () => {
    resetForm();
    setShow(true);
  };

  const openEdit = (a: Article) => {
    setEditing(a);
    setTitle(a.title);
    setContent(a.content);
    setShow(true);
  };

  const load = async () => {
    setErr("");
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/api/knowledge`, { credentials: "include" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setErr(e?.message || t("knowledge.loadError"));
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [i18n.language]);

  const save = async () => {
    if (!title.trim()) return;

    try {
      const url = editing
        ? `${BASE_URL}/api/knowledge/${editing.id}`
        : `${BASE_URL}/api/knowledge`;
      const method = editing ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setShow(false);
      resetForm();
      await load();
    } catch (e: any) {
      alert(e?.message || t("knowledge.saveError"));
    }
  };

  const remove = async (id: number) => {
    if (!confirm(t("knowledge.deleteConfirm"))) return;
    try {
      const res = await fetch(`${BASE_URL}/api/knowledge/${id}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await load();
    } catch (e: any) {
      alert(e?.message || t("knowledge.deleteError"));
    }
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="m-0">{t("knowledge.title")}</h3>
        {canEdit && (
          <Button onClick={openCreate}>{t("knowledge.new")}</Button>
        )}
      </div>

      {err && <Alert variant="danger">{t("common.error")}: {err}</Alert>}

      {loading ? (
        <div className="text-center my-5"><Spinner animation="border" /></div>
      ) : (
        <div className="row g-3">
          {items.length === 0 && <div className="text-muted">{t("common.empty")}</div>}
          {items.map((a) => (
            <div className="col-lg-6" key={a.id}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start gap-3">
                    <div>
                      <h5 className="mb-2">{a.title}</h5>
                      <div className="text-muted small mb-2">
                        {a.created_at ? new Date(a.created_at).toLocaleString() : ""}
                      </div>
                    </div>
                    {canEdit && (
                      <div className="btn-group">
                        <Button size="sm" variant="outline-primary" onClick={() => openEdit(a)}>
                          {t("common.edit")}
                        </Button>
                        <Button size="sm" variant="outline-danger" onClick={() => remove(a.id)}>
                          {t("common.delete")}
                        </Button>
                      </div>
                    )}
                  </div>
                  <div style={{ whiteSpace: "pre-wrap" }}>{a.content}</div>
                </Card.Body>
              </Card>
            </div>
          ))}
        </div>
      )}

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{editing ? t("knowledge.editTitle") : t("knowledge.newTitle")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={(e) => { e.preventDefault(); save(); }}>
            <Form.Group className="mb-3">
              <Form.Label>{t("knowledge.form.title")}</Form.Label>
              <Form.Control
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group>
              <Form.Label>{t("knowledge.form.content")}</Form.Label>
              <Form.Control
                as="textarea"
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>{t("common.cancel")}</Button>
          <Button onClick={save}>{t("common.save")}</Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
