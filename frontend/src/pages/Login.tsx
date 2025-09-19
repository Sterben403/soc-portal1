import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { kcRegisterUrl } from "../lib/auth";

function extractErrorMessage(err: any): string {
  try {
    // axios: при сетевой ошибке err.response отсутствует
    const r = err?.response;
    const d = r?.data;
    const detail = d?.detail ?? d;

    if (typeof detail === "string") return detail;
    if (detail?.error_description) return String(detail.error_description);
    if (detail?.error) return String(detail.error);

    if (detail != null) {
      try { return JSON.stringify(detail); } catch {}
    }

    // fallback’и:
    if (err?.message) return String(err.message);
    return "Network error";
  } catch {
    return "Network error";
  }
}

function looksLikeOtpNeeded(msg?: string) {
  const m = (msg || "").toLowerCase();
  return (
    m.includes("otp") ||
    m.includes("totp") ||
    m.includes("authenticator") ||
    m.includes("two-factor") ||
    m.includes("2fa")
  );
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [askOtp, setAskOtp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { signIn } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signIn(email, password, askOtp && otp ? otp : undefined);
      navigate("/dashboard");
    } catch (err: any) {
      const msg = extractErrorMessage(err);
      setError(msg);
      if (looksLikeOtpNeeded(msg)) setAskOtp(true);
    } finally {
      setLoading(false);
    }
  };

  const goRegister = async () => {
    try {
      const url = await kcRegisterUrl(); // <- ждём Promise<string>
      window.location.href = url;
    } catch (err) {
      console.error(err);
      alert("Failed to build register URL");
    }
  };

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <div className="d-flex justify-content-between align-items-center mt-3 mb-4">
        <h3 className="mb-0">{t("auth.login")}</h3>
        <LanguageSwitcher />
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={onSubmit}>
        <div className="mb-3">
          <label className="form-label">{t("auth.email")}</label>
          <input
            className="form-control"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">{t("auth.password")}</label>
          <input
            className="form-control"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        {askOtp && (
          <div className="mb-3">
            <label className="form-label">Код из приложения (OTP)</label>
            <input
              className="form-control"
              type="text"
              inputMode="numeric"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="123456"
            />
          </div>
        )}

        <button type="submit" className="btn btn-primary w-100" disabled={loading}>
          {loading ? t("common.loading") : t("auth.loginButton")}
        </button>

        <div className="text-center mt-3">
          {t("auth.noAccount")}{" "}
          <button
            type="button"
            className="btn btn-link p-0 align-baseline"
            onClick={goRegister}
          >
            {t("auth.register")}
          </button>
        </div>
      </form>
    </div>
  );
}
