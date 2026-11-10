import { Suspense, lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { RedirectIfAuthenticated, RequireAuth } from "./auth/AuthContext";
import Logo from "./components/ui/Logo";

const AuthPage = lazy(() => import("./pages/AuthPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));

function PageLoader() {
  return (
    <div className="page-loader" role="status" aria-label="Carregando">
      <Logo showName={false} />
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Navigate to="/painel" replace />} />
        <Route path="/cadastro" element={<RedirectIfAuthenticated><AuthPage mode="signup" /></RedirectIfAuthenticated>} />
        <Route path="/entrar" element={<RedirectIfAuthenticated><AuthPage mode="login" /></RedirectIfAuthenticated>} />
        <Route path="/painel" element={<RequireAuth><DashboardPage /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/painel" replace />} />
      </Routes>
    </Suspense>
  );
}
