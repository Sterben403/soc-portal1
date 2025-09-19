// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import PrivateLayout from "./components/PrivateLayout";
import Knowledge from "./pages/Knowledge";
import Dashboard from "./pages/Dashboard";
import Incidents from "./pages/Incidents";
import Notifications from "./pages/Notifications";
import Reports from "./pages/Reports";
import Tickets from "./pages/Tickets";
import Login from "./pages/Login";
import IncidentDetails from "./pages/IncidentDetails";
import TicketDetail from "./pages/TicketDetail";
import AnalystDashboard from "./pages/analyst-only/AnalystDashboard";
import { useAuth } from "./context/AuthContext";
import ManagerDashboard from "./pages/manager-only/ManagerDashboard";
import AuthCallback from "./pages/AuthCallback";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import RoleApprovals from "./pages/admin/RoleApprovals";

const App = () => {
  const { currentUser } = useAuth();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />

        {/* Защищённая обёртка */}
        <Route element={<PrivateLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/incidents/:id" element={<IncidentDetails />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/tickets/:ticketId" element={<TicketDetail />} />
          <Route path="/knowledge" element={<Knowledge />} />

          {/* Для аналитика */}
          <Route
            path="/analyst-only/dashboard"
            element={currentUser?.role === "analyst" ? <AnalystDashboard /> : <Navigate to="/" />}
          />

          {/* Админ */}
          <Route
            path="/admin/role-approvals"
            element={currentUser?.role === "admin" ? <RoleApprovals /> : <Navigate to="/" />}
          />

          {/* Для менеджера */}
          <Route
            path="/manager-only/dashboard"
            element={currentUser?.role === "manager" ? <ManagerDashboard /> : <Navigate to="/" />}
          />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
