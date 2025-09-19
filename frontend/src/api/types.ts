export interface Ticket {
  id: number;
  title: string;
  category: string;
  status: "open" | "pending" | "closed";
  created_at: string;
  client_id: number;
}

export interface TicketMessage {
  id: number;
  ticket_id: number;
  sender_id: number;
  sender_role: "client" | "analyst" | "manager";
  message: string;
  created_at: string;
}

export interface CreateTicketData {
  title: string;
  category: string;
  message: string;
}