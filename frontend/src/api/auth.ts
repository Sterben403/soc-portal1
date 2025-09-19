import api from "./http";

const KEY = "kc_access_token";

export const saveToken = (t: string) => localStorage.setItem(KEY, t);
export const readToken = () => localStorage.getItem(KEY);
export const clearToken = () => localStorage.removeItem(KEY);

// Теперь логин принимает ещё и otp (необязательно)
export const login = async (payload: { email: string; password: string; otp?: string }) => {
  const { data } = await api.post("/auth/login", payload, { withCredentials: true });
  return data as { access_token: string; token_type: string };
};

export const me = async () => {
  const { data } = await api.get("/auth/kc/me", { withCredentials: true });
  return data;
};

export const logout = async () => {
  await api.post("/auth/logout", null, { withCredentials: true });
};
