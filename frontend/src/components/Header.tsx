import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useRoleAccess } from "../hooks/useRoleAccess";
import "./Header.css";
import { useEffect, useState } from "react";
import { getPendingCount } from "../api/roles";
import { useTranslation } from "react-i18next";
import ProfileMenu from "./ProfileMenu";

const Header = () => {
  const { currentUser } = useAuth();
  const { canViewReports } = useRoleAccess();
  const { t } = useTranslation();

  const isAdmin = currentUser?.role === "admin";
  const [pending, setPending] = useState(0);

  useEffect(() => {
    if (!isAdmin) return;
    let mounted = true;
    const load = async () => {
      try {
        const n = await getPendingCount();
        if (mounted) setPending(n);
      } catch {}
    };
    load();
    const id = setInterval(load, 20000);
    return () => { mounted = false; clearInterval(id); };
  }, [isAdmin]);

  return (
    <header className="modern-header px-4 py-2">
      <div className="header-flex d-flex align-items-center justify-content-between">
        <div className="fw-bold fs-5">SOC Portal</div>

        <nav className="header-center-nav d-flex gap-2">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.dashboard')}</NavLink>
          <NavLink to="/incidents" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.incidents')}</NavLink>
          <NavLink to="/notifications" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.notifications')}</NavLink>
          <NavLink to="/knowledge" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.knowledge')}</NavLink>
          {canViewReports && (
            <NavLink to="/reports" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.reports')}</NavLink>
          )}
          <NavLink to="/tickets" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>{t('navigation.tickets')}</NavLink>
          {isAdmin && (
            <NavLink to="/admin/role-approvals" className={({ isActive }) => isActive ? "nav-link-modern active" : "nav-link-modern"}>
              {t('navigation.admin')}{pending > 0 ? ` (${pending})` : ""}
            </NavLink>
          )}
        </nav>

        {currentUser && (
          <div className="d-flex align-items-center gap-2">
            {/* вместо LanguageSwitcher — меню профиля со сменой языка */}
            <ProfileMenu />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
