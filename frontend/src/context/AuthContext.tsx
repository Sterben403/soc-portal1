import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { login as apiLogin, me as apiMe, logout as apiLogout, readToken, saveToken, clearToken } from "../api/auth";
import { setTokenGetter } from "../api/http";

type User = { id?: string; email: string; role?: string; username?: string };
type AuthCtx = {
  currentUser: User | null;
  loading: boolean;
  signIn: (email: string, password: string, otp?: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const Ctx = createContext<AuthCtx>({} as AuthCtx);
export const useAuth = () => useContext(Ctx);

// Нормализуем имена ролей, если вдруг в KC они с префиксом soc_
const pickRole = (roles: string[] = []) => {
  const normalized = new Set(roles.map(r => r.replace(/^soc_/, "")));
  return ["admin", "manager", "analyst", "client"].find(r => normalized.has(r)) ?? "client";
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = readToken();
    if (stored) {
      setTokenGetter(() => stored);
      apiMe()
        .then((p: any) => {
          setCurrentUser({
            id: p.sub,
            email: p.email,
            username: p.email,
            role: pickRole(p.roles || []),
          });
        })
        .catch(() => {
          clearToken();
          setTokenGetter(null);
          setCurrentUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setTokenGetter(null);
      setLoading(false);
    }
  }, []);

  const signIn = async (email: string, password: string, otp?: string) => {
    const { access_token } = await apiLogin({ email, password, otp });
    saveToken(access_token);
    setTokenGetter(() => access_token);
    const p: any = await apiMe();
    setCurrentUser({
      id: p.sub,
      email: p.email,
      username: p.email,
      role: pickRole(p.roles || []),
    });
  };

  const signOut = async () => {
    await apiLogout().catch(() => {});
    clearToken();
    setTokenGetter(null);
    setCurrentUser(null);
  };

  const value = useMemo(() => ({ currentUser, loading, signIn, signOut }), [currentUser, loading]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
