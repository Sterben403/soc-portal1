import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { requestRole } from "../api/roles";
import { Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function Profile() {
  const { currentUser } = useAuth();
  const [role, setRole] = useState<"analyst"|"manager">("analyst");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const { t } = useTranslation();

  if (currentUser?.role === "admin") {
    return <Navigate to="/admin/role-approvals" replace />;
  }

  if (currentUser?.role === "analyst" || currentUser?.role === "manager") {
    return (
      <div className="container" style={{maxWidth:520}}>
        <h3 className="mt-4">{t("profile.title")}</h3>
        <div className="text-muted mb-3">
          {currentUser?.email} — {t("profile.role")}: <b>{t(`roles.${currentUser?.role}`)}</b>
        </div>
        <div className="alert alert-success">
          {t("profile.alreadyUpgraded")}
        </div>
      </div>
    );
  }

  const send = async () => {
    setBusy(true); setMsg(null);
    try {
      await requestRole(role);
      setMsg(t("profile.requestSent"));
    } catch (e:any) {
      setMsg(e?.response?.data?.detail || t("common.error"));
    } finally { setBusy(false); }
  };

  return (
    <div className="container" style={{maxWidth:520}}>
      <h3 className="mt-4">{t("profile.title")}</h3>
      <div className="text-muted mb-3">
        {currentUser?.email} — {t("profile.role")}: {t(`roles.${currentUser?.role || "client"}`)}
      </div>

      <div className="card p-3">
        <div className="fw-semibold mb-2">{t("profile.askForUpgrade")}</div>
        <select className="form-select mb-2" value={role} onChange={e => setRole(e.target.value as any)}>
          <option value="analyst">{t("roles.analyst")}</option>
          <option value="manager">{t("roles.managerRo")}</option>
        </select>
        <button className="btn btn-primary" onClick={send} disabled={busy}>
          {busy ? t("common.sending") : t("profile.requestRoleBtn")}
        </button>
        {msg && <div className="alert alert-info mt-3">{msg}</div>}
      </div>
    </div>
  );
}
