import { useAuth } from "../context/AuthContext";

/**
 * Утилитный хук для проверки прав по ролям.
 * Роли: "client" | "analyst" | "manager"
 */
export const useRoleAccess = () => {
  const { currentUser } = useAuth();
  const role = currentUser?.role ?? null;

  const isClient = role === "client";
  const isAnalyst = role === "analyst";
  const isManager = role === "manager";

  // Видимость разделов
  const canViewReports = isAnalyst || isManager;
  const canViewNotifications = isClient || isAnalyst || isManager;

  // Действия по инцидентам
  const canManageIncidents = isAnalyst;              // закрывать/переоткрывать
  const canConfirmIncidents = isClient;              // подтверждать клиентом
  const canReopenIncidents = isAnalyst || isManager; // переоткрывать

  // Тикеты
  const canCreateTickets = isClient;                 // создавать тикеты клиент
  const canReplyTickets = isClient || isAnalyst;     // отвечать клиент/аналитик
  const canViewAllTickets = isAnalyst || isManager;  // просмотр всех (если нужно)

  return {
    role,
    isClient,
    isAnalyst,
    isManager,
    canViewReports,
    canViewNotifications,
    canManageIncidents,
    canConfirmIncidents,
    canReopenIncidents,
    canCreateTickets,
    canReplyTickets,
    canViewAllTickets,
  };
};
