import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { NavLink, useNavigate } from "react-router-dom";
import { useRoleAccess } from "../hooks/useRoleAccess";
import { useEffect, useRef, useState } from "react";

const LANGS = [
  { code: "en", label: "EN" },
  { code: "ru", label: "RU" },
  { code: "kk", label: "KK" },
];

export default function ProfileMenu() {
  const { t, i18n } = useTranslation();
  const { currentUser, signOut } = useAuth();
  const { canViewReports } = useRoleAccess();
  const isAdmin = currentUser?.role === "admin";
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!ref.current) return;
      if (!ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("click", onDoc);
    return () => document.removeEventListener("click", onDoc);
  }, []);

  return (
    <div className="dropdown" ref={ref}>
      <button
        className="btn btn-light border rounded-pill px-3 py-1 d-flex align-items-center gap-2"
        onClick={() => setOpen(v => !v)}
      >
        <span className="small text-muted">{t("header.signedAs")}</span>
        <span className="fw-semibold">{currentUser?.username || currentUser?.email}</span>
        <i className="bi bi-chevron-down" />
      </button>

      <ul className={`dropdown-menu dropdown-menu-end shadow ${open ? "show" : ""}`} style={{ minWidth: 260 }}>
        {isAdmin && (
          <>
            <li className="dropdown-header">{t("header.adminSection")}</li>
            <li>
              <NavLink className="dropdown-item" to="/admin/role-approvals" onClick={() => setOpen(false)}>
                {t("navigation.admin")}
              </NavLink>
            </li>
            <li><hr className="dropdown-divider" /></li>
          </>
        )}

        {!isAdmin && (
          <>
            <li className="dropdown-header">{t("header.account")}</li>
            <li>
              <NavLink className="dropdown-item" to="/profile#request-role" onClick={() => setOpen(false)}>
                <i className="bi bi-person-plus me-2" />
                {t("profile.requestRole")}
              </NavLink>
            </li>
            {canViewReports && (
              <li>
                <NavLink className="dropdown-item" to="/reports" onClick={() => setOpen(false)}>
                  <i className="bi bi-graph-up me-2" />
                  {t("navigation.reports")}
                </NavLink>
              </li>
            )}
            <li><hr className="dropdown-divider" /></li>
          </>
        )}

        <li className="dropdown-header">{t("header.language")}</li>
        <li className="px-3 py-2">
          <div className="btn-group w-100" role="group" aria-label="Language switch">
            {LANGS.map(l => (
              <button
                key={l.code}
                className={`btn btn-sm ${i18n.language?.startsWith(l.code) ? "btn-primary" : "btn-outline-primary"}`}
                onClick={() => i18n.changeLanguage(l.code)}
              >
                {l.label}
              </button>
            ))}
          </div>
        </li>

        <li><hr className="dropdown-divider" /></li>
        <li>
          <button
            className="dropdown-item text-danger"
            onClick={async () => { await signOut(); navigate("/login"); }}
          >
            <i className="bi bi-box-arrow-right me-2" />
            {t("auth.logoutButton")}
          </button>
        </li>
      </ul>
    </div>
  );
}
