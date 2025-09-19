import { Navigate, Outlet } from "react-router-dom";
import Layout from "./Layout";
import { useAuth } from "../context/AuthContext";

const PrivateLayout = () => {
  const { currentUser, loading } = useAuth();

  if (loading) return <div className="p-4">Loading…</div>;
  if (!currentUser) return <Navigate to="/login" replace />;

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

export default PrivateLayout;
