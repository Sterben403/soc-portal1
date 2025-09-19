import { useState } from "react";
import { Button, Form, Spinner, Alert, Modal } from "react-bootstrap";
import { createTicket } from "../api/api";
import { useTranslation } from "react-i18next";

interface Props {
  onCreated: () => void;
}

const CreateTicketForm = ({ onCreated }: Props) => {
  const { t } = useTranslation();

  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const resetForm = () => {
    setTitle("");
    setCategory("");
    setMessage("");
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // backend ЖДЁТ значения из этого списка (на русском)!
      await createTicket({
        title,
        message,
        category,
      });

      onCreated();
      resetForm();
      setShowModal(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : t("tickets.errors.createFailed")
      );
    } finally {
      setLoading(false);
    }
  };

  // Ровно те значения, которые объявлены в Enum на бэке (app/schemas/ticket.py)
  const rawCategories = [
    "Вопрос",
    "Ошибка",
    "Инцидент",
    "Запрос на источник",
  ];

  return (
    <>
      <Button variant="primary" onClick={() => setShowModal(true)} className="mb-3">
        {t("tickets.createNew")}
      </Button>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{t("tickets.newTicket")}</Modal.Title>
          </Modal.Header>

          <Modal.Body>
            {error && <Alert variant="danger">{error}</Alert>}

            <Form.Group className="mb-3" controlId="ticketTitle">
              <Form.Label>{t("tickets.field.title")}</Form.Label>
              <Form.Control
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t("tickets.placeholder.short")}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="ticketCategory">
              <Form.Label>{t("tickets.field.category")}</Form.Label>
              <Form.Select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                required
              >
                <option value="">{t("tickets.field.chooseCategory")}</option>
                {rawCategories.map((val) => (
                  <option key={val} value={val}>
                    {/* подпись локализуем, значение – оригинальное */}
                    {t(`tickets.categories.${val}`, val)}
                  </option>
                ))}
              </Form.Select>
              <Form.Text className="text-muted">
                {t("tickets.categoryHint")}
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3" controlId="ticketMessage">
              <Form.Label>{t("tickets.field.description")}</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={t("tickets.placeholder.long")}
                required
              />
            </Form.Group>
          </Modal.Body>

          <Modal.Footer>
            <Button
              variant="secondary"
              onClick={() => {
                setShowModal(false);
                resetForm();
              }}
              disabled={loading}
            >
              {t("common.cancel")}
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Spinner size="sm" animation="border" className="me-2" />
                  {t("common.sending")}
                </>
              ) : (
                t("tickets.create")
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};

export default CreateTicketForm;
