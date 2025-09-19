import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function AuthCallback() {
  const nav = useNavigate();
  const { t } = useTranslation();
  useEffect(() => {
    nav("/", { replace: true });
  }, [nav]);
  return <div className="p-4">{t("auth.returning")}…</div>;
}
