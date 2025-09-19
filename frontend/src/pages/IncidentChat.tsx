import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Alert, Button, Form, Spinner } from "react-bootstrap";
import { getMessages, sendMessage } from "../api/api";
import { useTranslation } from "react-i18next";

type ChatMessage = {
  id: number;
  message: string;
  sender_role: string;
  created_at: string;
};

const IncidentChat = () => {
  const { id } = useParams<{ id: string }>();
  const incidentId = Number(id);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { t } = useTranslation();

  const loadMessages = async () => {
    setLoading(true);
    setError("");
    try {
      const data = (await getMessages(incidentId)) as ChatMessage[];
      setMessages(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e?.message || (t("incidents.chat.loadError") as string));
    } finally {
      setLoading(false);
    }
  };

  const send = async () => {
    if (!newMessage.trim()) return;
    try {
      const form = new FormData();
      form.append("incident_id", String(incidentId));
      form.append("message", newMessage.trim());
      await sendMessage(incidentId, form);
      setNewMessage("");
      await loadMessages();
    } catch (e: any) {
      setError(e?.message || (t("incidents.chat.sendError") as string));
    }
  };

  useEffect(() => {
    if (incidentId) loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  return (
    <div className="container mt-4">
      <h4>{t("incidents.chat.title", { id })}</h4>
      {error && <Alert variant="danger">{error}</Alert>}
      {loading ? (
        <Spinner animation="border" />
      ) : (
        <div className="border rounded p-3 mb-3" style={{ maxHeight: 400, overflowY: "auto" }}>
          {messages.map((msg) => (
            <div key={msg.id} className="mb-2">
              <strong>{msg.sender_role}:</strong> {msg.message}
              <div className="small text-muted">{new Date(msg.created_at).toLocaleString()}</div>
            </div>
          ))}
          {messages.length === 0 && (
            <div className="text-muted">{t("incidents.chat.empty")}</div>
          )}
        </div>
      )}

      <Form.Control
        placeholder={(t("incidents.chat.placeholder") as string) || "Message…"}
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
      />
      <Button className="mt-2" onClick={send}>
        {t("common.send")}
      </Button>
    </div>
  );
};
export default IncidentChat;
