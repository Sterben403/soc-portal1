import { useEffect, useState } from "react";
import { fetchNotifications } from "../api/api";
import { Spinner, Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";

interface Notification {
  id: number;
  channel: string;
  target: string;
  event: string;
  created_at: string;
}

const Notifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filtered, setFiltered] = useState<Notification[]>([]);
  const [filterType, setFilterType] = useState("all");
  const [sortOrder, setSortOrder] = useState("desc");
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchNotifications();
      setNotifications(data);
    } catch (e) {
      alert(t("notifications.loadError"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    let data = [...notifications];
    if (filterType !== "all") data = data.filter((n) => n.channel === filterType);
    data.sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return sortOrder === "asc" ? dateA - dateB : dateB - dateA;
    });
    setFiltered(data);
  }, [filterType, sortOrder, notifications]);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>{t("notifications.title")}</h4>
        <Button variant="secondary" onClick={load}>{t("common.refresh")}</Button>
      </div>

      <div className="d-flex gap-3 mb-3">
        <Form.Select value={filterType} onChange={(e) => setFilterType(e.target.value)} style={{ maxWidth: 200 }}>
          <option value="all">{t("notifications.filters.all")}</option>
          <option value="email">Email</option>
          <option value="telegram">Telegram</option>
          <option value="webhook">Webhook</option>
        </Form.Select>

        <Form.Select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)} style={{ maxWidth: 200 }}>
          <option value="desc">{t("notifications.sort.newFirst")}</option>
          <option value="asc">{t("notifications.sort.oldFirst")}</option>
        </Form.Select>
      </div>

      {loading ? (
        <Spinner animation="border" />
      ) : (
        <ul className="list-group">
          {filtered.map((n) => (
            <li key={n.id} className="list-group-item d-flex justify-content-between">
              <div>
                <strong>{n.channel.toUpperCase()}:</strong> {n.event}
              </div>
              <small>{new Date(n.created_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Notifications;
