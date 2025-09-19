import { useState } from "react";
import type { FormEvent } from "react";
import { replyToTicket } from "../api/api";
import { Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";

interface Props {
  ticketId: number;
  onReplied: () => void;
}

const TicketReplyForm: React.FC<Props> = ({ ticketId, onReplied }) => {
  const [message, setMessage] = useState<string>("");
  const { t } = useTranslation();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    try {
      await replyToTicket(ticketId, message);
      setMessage("");
      onReplied();
    } catch {
      alert(t("tickets.replyError"));
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mt-3">
      <Form.Group className="mb-2">
        <Form.Control
          as="textarea"
          rows={3}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={t("tickets.replyPlaceholder") as string}
        />
      </Form.Group>
      <Button type="submit" disabled={!message.trim()}>
        {t("common.send")}
      </Button>
    </Form>
  );
};

export default TicketReplyForm;
