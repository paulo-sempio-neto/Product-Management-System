import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "motion/react";
import { Lock, Mail, Store, User } from "lucide-react";
import { Suspense, lazy, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { AuthError, EMAIL_PATTERN, measurePassword } from "../auth/authService";
import Button from "../components/ui/Button";
import ErrorBoundary from "../components/ui/ErrorBoundary";
import Field from "../components/ui/Field";
import Logo from "../components/ui/Logo";

const ShelfScene = lazy(() => import("../three/ShelfScene"));

type Mode = "signup" | "login";
type Errors = Partial<Record<"name" | "storeName" | "email" | "password" | "form", string>>;

function supportsWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

function StrengthMeter({ password }: { password: string }) {
  const { score, label } = measurePassword(password);
  if (!password) return <span>Use 8 ou mais caracteres, misturando letras e números.</span>;
  return (
    <span className="strength" data-score={score}>
      <span className="strength__bars" aria-hidden="true">
        {[1, 2, 3, 4].map((bar) => (
          <span key={bar} className={bar <= score ? "is-on" : ""} />
        ))}
      </span>
      <span>Senha {label.toLowerCase()}</span>
    </span>
  );
}

export default function AuthPage({ mode }: { mode: Mode }) {
  const { signup, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const reduceMotion = useReducedMotion();
  const webgl = useMemo(supportsWebGL, []);

  const [name, setName] = useState("");
  const [storeName, setStoreName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [errors, setErrors] = useState<Errors>({});
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [curtain, setCurtain] = useState<{ x: number; y: number } | null>(null);
  const submitRef = useRef<HTMLButtonElement>(null);

  // Warm up the dashboard bundle while the person fills in the form.
  useEffect(() => {
    const idle = window.requestIdleCallback ?? ((cb: () => void) => window.setTimeout(cb, 1200));
    idle(() => void import("./DashboardPage"));
  }, []);

  useEffect(() => {
    setErrors({});
    document.title = mode === "signup" ? "Criar conta · Gôndola" : "Entrar · Gôndola";
  }, [mode]);

  function validate(): Errors {
    const next: Errors = {};
    if (mode === "signup") {
      if (name.trim().length < 2) next.name = "Digite seu nome.";
      if (storeName.trim().length < 2) next.storeName = "Digite o nome do seu negócio.";
    }
    if (!EMAIL_PATTERN.test(email.trim())) next.email = "Digite um e-mail válido, como voce@loja.com.";
    if (mode === "signup" && password.length < 8) next.password = "A senha precisa ter pelo menos 8 caracteres.";
    if (mode === "login" && !password) next.password = "Digite sua senha.";
    return next;
  }

  function validateField(field: keyof Errors) {
    const result = validate();
    setErrors((current) => ({ ...current, [field]: result[field] }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const result = validate();
    setErrors(result);
    if (Object.keys(result).length > 0) return;

    setSubmitting(true);
    try {
      if (mode === "signup") {
        await signup({ name, storeName, email, password });
      } else {
        await login({ email, password, remember });
      }
      setDone(true);
      const rect = submitRef.current?.getBoundingClientRect();
      const origin = rect ? { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 } : { x: innerWidth / 2, y: innerHeight / 2 };
      const from = (location.state as { from?: string } | null)?.from ?? "/painel";
      window.setTimeout(() => setCurtain(origin), reduceMotion ? 0 : 450);
      window.setTimeout(() => navigate(from, { replace: true, state: { welcome: mode } }), reduceMotion ? 50 : 1150);
    } catch (error) {
      if (error instanceof AuthError) {
        setErrors({ [error.field ?? "form"]: error.message });
      } else {
        setErrors({ form: "Não foi possível concluir agora. Tente novamente em instantes." });
      }
      setSubmitting(false);
    }
  }

  const isSignup = mode === "signup";

  return (
    <div className="auth">
      <section className="auth__stage" aria-label="Apresentação">
        <div className="auth__stage-top">
          <Link to="/" className="auth__brand" aria-label="Gôndola, página inicial">
            <Logo tone="light" />
          </Link>
        </div>

        <div className="auth__scene">
          {webgl ? (
            <ErrorBoundary fallback={<div className="auth__scene-fallback" />}>
              <Suspense fallback={<div className="auth__scene-fallback" />}>
                <ShelfScene />
              </Suspense>
            </ErrorBoundary>
          ) : (
            <div className="auth__scene-fallback" />
          )}
        </div>

        <motion.div
          className="auth__pitch"
          initial={reduceMotion ? false : { opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.5, ease: [0.22, 1, 0.36, 1] }}
        >
          <h1>Seu catálogo, sempre na prateleira certa.</h1>
          <p>Cadastre, encontre e atualize produtos e preços em um só lugar — sem planilha, sem bagunça.</p>
        </motion.div>
      </section>

      <section className="auth__panel">
        <div className="auth__panel-inner">
          <LayoutGroup>
            <nav className="auth__switch" aria-label="Escolha como continuar">
              {(["signup", "login"] as const).map((item) => (
                <Link
                  key={item}
                  to={item === "signup" ? "/cadastro" : "/entrar"}
                  replace
                  state={location.state}
                  className={`auth__switch-item ${mode === item ? "is-active" : ""}`}
                  aria-current={mode === item ? "page" : undefined}
                >
                  {mode === item && (
                    <motion.span layoutId="auth-switch-pill" className="auth__switch-pill" transition={{ type: "spring", stiffness: 420, damping: 34 }} />
                  )}
                  <span className="auth__switch-label">{item === "signup" ? "Criar conta" : "Entrar"}</span>
                </Link>
              ))}
            </nav>
          </LayoutGroup>

          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={mode}
              initial={reduceMotion ? false : { opacity: 0, x: isSignup ? -16 : 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, x: isSignup ? 16 : -16 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            >
              <header className="auth__header">
                <h2>{isSignup ? "Crie sua conta" : "Que bom te ver de novo"}</h2>
                <p>
                  {isSignup
                    ? "Leva menos de um minuto. Depois é só cadastrar seus produtos."
                    : "Entre para ver e atualizar seus produtos."}
                </p>
              </header>

              <form className="auth__form" onSubmit={handleSubmit} noValidate>
                {isSignup && (
                  <div className="auth__row">
                    <Field
                      label="Seu nome"
                      icon={<User size={18} />}
                      autoComplete="name"
                      placeholder="Ana Souza"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      onBlur={() => name && validateField("name")}
                      error={errors.name}
                    />
                    <Field
                      label="Nome do negócio"
                      icon={<Store size={18} />}
                      autoComplete="organization"
                      placeholder="Mercadinho da Ana"
                      value={storeName}
                      onChange={(e) => setStoreName(e.target.value)}
                      onBlur={() => storeName && validateField("storeName")}
                      error={errors.storeName}
                    />
                  </div>
                )}

                <Field
                  label="E-mail"
                  type="email"
                  icon={<Mail size={18} />}
                  autoComplete="email"
                  inputMode="email"
                  placeholder="voce@loja.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => email && validateField("email")}
                  error={errors.email}
                />

                <Field
                  label="Senha"
                  revealable
                  icon={<Lock size={18} />}
                  autoComplete={isSignup ? "new-password" : "current-password"}
                  placeholder={isSignup ? "Mínimo de 8 caracteres" : "Sua senha"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={errors.password}
                  hint={isSignup ? <StrengthMeter password={password} /> : undefined}
                />

                {!isSignup && (
                  <label className="checkbox">
                    <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
                    <span className="checkbox__box" aria-hidden="true" />
                    Manter conectado neste dispositivo
                  </label>
                )}

                <AnimatePresence>
                  {errors.form && (
                    <motion.p className="auth__form-error" role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
                      {errors.form}
                    </motion.p>
                  )}
                </AnimatePresence>

                <Button ref={submitRef} type="submit" size="lg" loading={submitting} done={done} className="auth__submit">
                  {isSignup ? "Criar conta" : "Entrar"}
                </Button>
              </form>

              <p className="auth__alt">
                {isSignup ? "Já tem conta? " : "Ainda não tem conta? "}
                <Link to={isSignup ? "/entrar" : "/cadastro"} replace state={location.state}>
                  {isSignup ? "Entrar" : "Criar conta"}
                </Link>
              </p>
              {isSignup && <p className="auth__note">Sua conta fica salva neste navegador.</p>}
            </motion.div>
          </AnimatePresence>
        </div>
      </section>

      <AnimatePresence>
        {curtain && (
          <motion.div
            className="auth__curtain"
            aria-hidden="true"
            initial={{ clipPath: `circle(0px at ${curtain.x}px ${curtain.y}px)` }}
            animate={{ clipPath: `circle(150vmax at ${curtain.x}px ${curtain.y}px)` }}
            transition={{ duration: 0.7, ease: [0.65, 0, 0.35, 1] }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
