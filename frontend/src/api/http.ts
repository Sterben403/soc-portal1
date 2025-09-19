import axios from "axios";

type TokenGetter = () => string | null;
let tokenGetter: TokenGetter | null = null;

export const setTokenGetter = (getter: TokenGetter | null) => {
  tokenGetter = getter;
};

// Все наши запросы идут на http://<BACKEND>/api/...
// => в .env фронта должен быть VITE_API_BASE = http://localhost:8000 (БЕЗ /api)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || window.location.origin,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const t = tokenGetter?.();
  if (t) {
    config.headers = config.headers ?? {};
    (config.headers as any).Authorization = `Bearer ${t}`;
  }

  // CSRF для небезопасных методов, если нет Bearer
  const method = (config.method || "get").toUpperCase();
  const isUnsafe = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
  if (!t && isUnsafe) {
    const m = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/);
    if (m) {
      try {
        const value = decodeURIComponent(m[1]);
        const nonce = value.split(".")[0];
        (config.headers as any)["X-CSRF-Token"] = nonce;
      } catch {}
    }
  }
  return config;
});

export default api;
