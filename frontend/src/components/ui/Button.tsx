import { motion, type HTMLMotionProps } from "motion/react";
import { Check } from "lucide-react";
import type { ReactNode } from "react";

type ButtonProps = Omit<HTMLMotionProps<"button">, "children"> & {
  variant?: "primary" | "ghost" | "danger" | "quiet";
  size?: "md" | "lg" | "sm";
  loading?: boolean;
  done?: boolean;
  icon?: ReactNode;
  children?: ReactNode;
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  done = false,
  icon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <motion.button
      whileTap={disabled || loading ? undefined : { scale: 0.97 }}
      className={`btn btn--${variant} btn--${size} ${className ?? ""}`}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      <span className={`btn__content ${loading || done ? "is-hidden" : ""}`}>
        {icon}
        {children}
      </span>
      {loading && !done && <span className="btn__spinner" aria-hidden="true" />}
      {done && (
        <motion.span
          className="btn__done"
          initial={{ scale: 0.4, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 500, damping: 22 }}
          aria-hidden="true"
        >
          <Check size={20} strokeWidth={3} />
        </motion.span>
      )}
    </motion.button>
  );
}
