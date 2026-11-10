import { Navigate, Route, Routes } from "react-router-dom";

import { RedirectIfAuthenticated, RequireAuth, useAuth } from "./auth/AuthContext";
import Button from "./components/ui/Button";
import Logo from "./components/ui/Logo";
import AuthPage from "./pages/AuthPage";
import LegacyDashboard from "./pages/LegacyDashboard";

function DashboardShell() {
  const { session, logout } = useAuth();
  return (
    <>
      <div className="interim-bar">
        <Logo />
        <div className="interim-bar__user">
          <span>{session?.user.storeName}</span>
          <Button variant="ghost" size="sm" onClick={logout}>
            Sair
          </Button>
        </div>
      </div>
      <LegacyDashboard />
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/painel" replace />} />
      <Route path="/cadastro" element={<RedirectIfAuthenticated><AuthPage mode="signup" /></RedirectIfAuthenticated>} />
      <Route path="/entrar" element={<RedirectIfAuthenticated><AuthPage mode="login" /></RedirectIfAuthenticated>} />
      <Route path="/painel" element={<RequireAuth><DashboardShell /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/painel" replace />} />
    </Routes>
  );
}
