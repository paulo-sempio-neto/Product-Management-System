import { Navigate, Route, Routes } from "react-router-dom";

import { RedirectIfAuthenticated, RequireAuth } from "./auth/AuthContext";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/painel" replace />} />
      <Route path="/cadastro" element={<RedirectIfAuthenticated><AuthPage mode="signup" /></RedirectIfAuthenticated>} />
      <Route path="/entrar" element={<RedirectIfAuthenticated><AuthPage mode="login" /></RedirectIfAuthenticated>} />
      <Route path="/painel" element={<RequireAuth><DashboardPage /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/painel" replace />} />
    </Routes>
  );
}
