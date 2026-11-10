import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { Navigate, useLocation } from "react-router-dom";

import * as authService from "./authService";
import type { LoginInput, Session, SignupInput } from "./authService";

type AuthContextValue = {
  session: Session | null;
  signup: (input: SignupInput) => Promise<Session>;
  login: (input: LoginInput) => Promise<Session>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => authService.getSession());

  const signup = useCallback(async (input: SignupInput) => {
    const next = await authService.signup(input);
    setSession(next);
    return next;
  }, []);

  const login = useCallback(async (input: LoginInput) => {
    const next = await authService.login(input);
    setSession(next);
    return next;
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setSession(null);
  }, []);

  const value = useMemo(() => ({ session, signup, login, logout }), [session, signup, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { session } = useAuth();
  const location = useLocation();
  if (!session) return <Navigate to={authService.hasAccounts() ? "/entrar" : "/cadastro"} replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}

export function RedirectIfAuthenticated({ children }: { children: ReactNode }) {
  const { session } = useAuth();
  if (session) return <Navigate to="/painel" replace />;
  return <>{children}</>;
}
