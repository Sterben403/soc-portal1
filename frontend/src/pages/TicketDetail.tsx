import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Alert, Button, Card, Spinner } from "react-bootstrap";
import api from "../api/http";
import { useTranslation } from "react-i18next";

interface Ticket {
  id: number;
  title: string;
  description: string;
  status: string;   // "Открыт" | "В ожидании" | "Закрыт"
  category: string; // "Вопрос" | "Ошибка" | "Инцидент" | "Запрос на источник"
  created_at: string;
}

// Русские статусы -> коды для i18n
const RU_STATUS_TO_CODE: Record<string, "open" | "pending" | "closed"> = {
  "Открыт": "open",
  "В ожидании": "pending",
  "Закрыт": "closed",
};

const TicketDetail = () => {
  const { ticketId } = useParams<{ ticketId: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { t } = useTranslation();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get<Ticket>(`/api/tickets/${ticketId}`);
      setTicket(data);
    } catch (e: any) {
      setError(e?.message || (t("common.loadError") as string));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticketId]);

  if (loading) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" />
      </div>
    );
  }
  if (error) return <Alert variant="danger">{t("common.error")}: {error}</Alert>;
  if (!ticket) return <Alert variant="warning">{t("tickets.notFound")}</Alert>;

  // Локализованная категория: ключ = русское значение из бэка
  const categoryLabel = t(`tickets.categories.${ticket.category}`, ticket.category);

  // Локализованный статус
  const statusCode = RU_STATUS_TO_CODE[ticket.status];
  const statusLabel = statusCode ? t(`tickets.filters.${statusCode}`) : ticket.status;

  return (
    <div className="container mt-4">
      <Card>
        <Card.Body>
          <h4>{ticket.title}</h4>
          <p>{ticket.description}</p>
          <p><strong>{t("tickets.category")}:</strong> {categoryLabel}</p>
          <p><strong>{t("tickets.status")}:</strong> {statusLabel}</p>
          <p><small className="text-muted">{new Date(ticket.created_at).toLocaleString()}</small></p>
        </Card.Body>
      </Card>
      <Button variant="outline-primary" className="mt-3" onClick={load}>
        {t("common.refresh")}
      </Button>
    </div>
  );
};

export default TicketDetail;
