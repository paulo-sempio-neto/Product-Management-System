import { AnimatePresence, motion } from "motion/react";
import { CircleAlert, CircleCheck, X } from "lucide-react";
import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";

type ToastTone = "success" | "error";
type Toast = {
  id: number;
  tone: ToastTone;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
};

type ToastInput = Omit<Toast, "id">;
const ToastContext = createContext<((toast: ToastInput) => void) | null>(null);

const DURATION = 5200;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);

  const dismiss = useCallback((id: number) => setToasts((list) => list.filter((t) => t.id !== id)), []);

  const push = useCallback(
    (toast: ToastInput) => {
      const id = nextId.current++;
      setToasts((list) => [...list.slice(-3), { ...toast, id }]);
      window.setTimeout(() => dismiss(id), DURATION);
    },
    [dismiss],
  );

  const value = useMemo(() => push, [push]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toasts" role="region" aria-label="Notificações" aria-live="polite">
        <AnimatePresence initial={false}>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              layout
              className={`toast toast--${toast.tone}`}
              role={toast.tone === "error" ? "alert" : "status"}
              initial={{ opacity: 0, y: 24, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 40, transition: { duration: 0.2 } }}
              transition={{ type: "spring", stiffness: 420, damping: 32 }}
            >
              <span className="toast__icon" aria-hidden="true">
                {toast.tone === "success" ? <CircleCheck size={20} /> : <CircleAlert size={20} />}
              </span>
              <div className="toast__body">
                <p className="toast__title">{toast.title}</p>
                {toast.description && <p className="toast__description">{toast.description}</p>}
              </div>
              {toast.action && (
                <button
                  type="button"
                  className="toast__action"
                  onClick={() => {
                    toast.action?.onClick();
                    dismiss(toast.id);
                  }}
                >
                  {toast.action.label}
                </button>
              )}
              <button type="button" className="toast__close" aria-label="Fechar notificação" onClick={() => dismiss(toast.id)}>
                <X size={16} />
              </button>
              <span className="toast__timer" style={{ animationDuration: `${DURATION}ms` }} aria-hidden="true" />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used inside <ToastProvider>");
  return context;
}
