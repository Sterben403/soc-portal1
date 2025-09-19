// src/pages/Notifications.tsx
import { useEffect, useState } from "react";
import { Spinner, Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { fetchNotifications } from "../api/api";

type Channel = "all" | "email" | "telegram" | "webhook";
type SortOrder = "asc" | "desc";

interface Notification {
  id: number;
  channel: Exclude<Channel, "all">;
  target: string;
  event: string;
  created_at: string;
}

export default function Notifications() {
  const { t } = useTranslation();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filtered, setFiltered] = useState<Notification[]>([]);
  const [filterType, setFilterType] = useState<Channel>("all");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [loading, setLoading] = useState<boolean>(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchNotifications();
      setNotifications(Array.isArray(data) ? data : []);
    } catch {
      alert(t("notifications.loadError"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const subset =
      filterType === "all"
        ? notifications
        : notifications.filter((n) => n.channel === filterType);

    subset.sort((a, b) => {
      const aTs = new Date(a.created_at).getTime();
      const bTs = new Date(b.created_at).getTime();
      return sortOrder === "asc" ? aTs - bTs : bTs - aTs;
    });

    setFiltered([...subset]);
  }, [notifications, filterType, sortOrder]);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="m-0">{t("notifications.title")}</h4>
        <Button variant="secondary" onClick={load}>
          {t("common.refresh")}
        </Button>
      </div>

      <div className="d-flex gap-3 mb-3">
        <Form.Select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as Channel)}
          style={{ maxWidth: 220 }}
          aria-label={t("notifications.filters.aria") || "Filter notifications"}
        >
          <option value="all">{t("notifications.filters.all")}</option>
          <option value="email">Email</option>
          <option value="telegram">Telegram</option>
          <option value="webhook">Webhook</option>
        </Form.Select>

        <Form.Select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as SortOrder)}
          style={{ maxWidth: 220 }}
          aria-label={t("notifications.sort.aria") || "Sort order"}
        >
          <option value="desc">{t("notifications.sort.new")}</option>
          <option value="asc">{t("notifications.sort.old")}</option>
        </Form.Select>
      </div>

      {loading ? (
        <Spinner animation="border" />
      ) : (
        <ul className="list-group">
          {filtered.map((n) => (
            <li
              key={n.id}
              className="list-group-item d-flex justify-content-between"
            >
              <div>
                <strong>{n.channel.toUpperCase()}:</strong> {n.event}
              </div>
              <small className="text-muted">
                {new Date(n.created_at).toLocaleString()}
              </small>
            </li>
          ))}
          {filtered.length === 0 && (
            <li className="list-group-item text-center text-muted">
              {t("common.noNotifications")}
            </li>
          )}
        </ul>
      )}
    </div>
  );
}
