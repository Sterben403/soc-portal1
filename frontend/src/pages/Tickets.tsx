import { useEffect, useState } from "react";
import { Button, Form, Spinner, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import api from "../api/http";
import CreateTicketForm from "./CreateTicketForm";
import { useTranslation } from "react-i18next";

interface Ticket {
  id: number;
  title: string;
  category: string; // приходит на русском: "Вопрос" | "Ошибка" | "Инцидент" | "Запрос на источник"
  status: string;   // приходит на русском: "Открыт" | "В ожидании" | "Закрыт"
  created_at: string;
}

// Маппинг русских статусов из бэка -> коды для i18n и логики
const RU_STATUS_TO_CODE: Record<string, "open" | "pending" | "closed" | undefined> = {
  "Открыт": "open",
  "В ожидании": "pending",
  "Закрыт": "closed",
};

const statusVariantByCode: Record<"open" | "pending" | "closed", string> = {
  open: "warning",
  pending: "info",
  closed: "success",
};

const Tickets = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [filtered, setFiltered] = useState<Ticket[]>([]);
  const [statusFilter, setStatusFilter] = useState<"all" | "open" | "pending" | "closed">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { t } = useTranslation();

  const loadTickets = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get<Ticket[]>("/api/tickets");
      setTickets(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err?.message || (t("common.unknownError") as string));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Фильтрация по коду статуса
  useEffect(() => {
    if (statusFilter === "all") {
      setFiltered(tickets);
    } else {
      setFiltered(
        tickets.filter((t) => RU_STATUS_TO_CODE[t.status] === statusFilter)
      );
    }
  }, [tickets, statusFilter]);

  const handleTicketClick = (ticketId: number) => navigate(`/tickets/${ticketId}`);

  // Рендер бейджа статуса с переводом
  const renderStatusBadge = (statusRu: string) => {
    const code = RU_STATUS_TO_CODE[statusRu];
    if (!code) {
      return <span className="badge bg-secondary">{statusRu}</span>;
    }
    const variant = statusVariantByCode[code] || "secondary";
    return (
      <span className={`badge bg-${variant}`}>
        {t(`tickets.filters.${code}`)}
      </span>
    );
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between mb-3">
        <h4>{t("tickets.title")}</h4>
        <Button onClick={loadTickets} variant="outline-primary">
          {loading ? <Spinner size="sm" /> : t("common.refresh")}
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <div className="mb-3">
        <Form.Select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value as "all" | "open" | "pending" | "closed")
          }
          style={{ maxWidth: 300 }}
        >
          <option value="all">{t("tickets.filters.all")}</option>
          <option value="open">{t("tickets.filters.open")}</option>
          <option value="pending">{t("tickets.filters.pending")}</option>
          <option value="closed">{t("tickets.filters.closed")}</option>
        </Form.Select>
      </div>

      <CreateTicketForm onCreated={loadTickets} />

      {loading ? (
        <div className="text-center my-4">
          <Spinner animation="border" />
        </div>
      ) : (
        <div className="list-group mt-3">
          {filtered.map((ticket) => (
            <button
              key={ticket.id}
              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              onClick={() => handleTicketClick(ticket.id)}
            >
              <div>
                {/* Категория через i18n-ключ по русскому значению */}
                <span className="badge bg-secondary me-2">
                  {t(`tickets.categories.${ticket.category}`, ticket.category)}
                </span>
                {ticket.title}
                <br />
                <small className="text-muted">
                  {t("tickets.status")}: {renderStatusBadge(ticket.status)}
                </small>
              </div>
              <small className="text-muted">
                {new Date(ticket.created_at).toLocaleString()}
              </small>
            </button>
          ))}
          {filtered.length === 0 && (
            <div className="list-group-item text-muted text-center">
              {t("tickets.empty")}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Tickets;
