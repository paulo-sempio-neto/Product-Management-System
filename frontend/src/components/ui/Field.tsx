import { AnimatePresence, motion } from "motion/react";
import { forwardRef, useId, useState, type InputHTMLAttributes, type ReactNode } from "react";
import { Eye, EyeOff } from "lucide-react";

type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  icon?: ReactNode;
  error?: string | null;
  hint?: ReactNode;
  revealable?: boolean;
};

const Field = forwardRef<HTMLInputElement, FieldProps>(function Field(
  { label, icon, error, hint, revealable, type = "text", className, ...props },
  ref,
) {
  const id = useId();
  const [revealed, setRevealed] = useState(false);
  const messageId = `${id}-message`;
  const inputType = revealable ? (revealed ? "text" : "password") : type;

  return (
    <div className={`field ${error ? "field--invalid" : ""} ${className ?? ""}`}>
      <label className="field__label" htmlFor={id}>
        {label}
      </label>
      <div className="field__control">
        {icon && <span className="field__icon" aria-hidden="true">{icon}</span>}
        <input
          ref={ref}
          id={id}
          type={inputType}
          aria-invalid={Boolean(error)}
          aria-describedby={error || hint ? messageId : undefined}
          className="field__input"
          {...props}
        />
        {revealable && (
          <button
            type="button"
            className="field__reveal"
            onClick={() => setRevealed((value) => !value)}
            aria-label={revealed ? "Ocultar senha" : "Mostrar senha"}
            aria-pressed={revealed}
          >
            {revealed ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      <AnimatePresence initial={false} mode="wait">
        {error ? (
          <motion.p
            key="error"
            id={messageId}
            className="field__message field__message--error"
            role="alert"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.18 }}
          >
            {error}
          </motion.p>
        ) : hint ? (
          <motion.div key="hint" id={messageId} className="field__message" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {hint}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
});

export default Field;
