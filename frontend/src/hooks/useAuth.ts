import { useAuth as useAuthCtx } from "../context/AuthContext";

export const useAuth = () => {
  const { currentUser, loading, signOut } = useAuthCtx();

  return {
    email: currentUser?.email ?? null,
    role: currentUser?.role ?? null,
    loading,
    isAuthenticated: !!currentUser,
    logout: () => signOut(),
  };
};
