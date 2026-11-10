import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, LogOut } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import type { User } from "../../auth/authService";
import Logo from "../ui/Logo";

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export default function Topbar({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [open, setOpen] = useState(false);
  const menu = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const close = (event: MouseEvent | KeyboardEvent) => {
      if (event instanceof KeyboardEvent && event.key !== "Escape") return;
      if (event instanceof MouseEvent && menu.current?.contains(event.target as Node)) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);

  return (
    <header className="topbar">
      <div className="topbar__inner">
        <Logo />
        <div className="account" ref={menu}>
          <button
            type="button"
            className="account__trigger"
            aria-haspopup="menu"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
          >
            <span className="avatar" aria-hidden="true">
              {initials(user.name)}
            </span>
            <span className="account__name">{user.name.split(" ")[0]}</span>
            <ChevronDown size={16} className={`account__chevron ${open ? "is-open" : ""}`} aria-hidden="true" />
          </button>
          <AnimatePresence>
            {open && (
              <motion.div
                className="account__menu"
                role="menu"
                initial={{ opacity: 0, y: -6, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.97 }}
                transition={{ duration: 0.16 }}
              >
                <div className="account__card">
                  <strong>{user.name}</strong>
                  <span>{user.email}</span>
                  <span>{user.storeName}</span>
                </div>
                <button type="button" role="menuitem" className="account__item" onClick={onLogout}>
                  <LogOut size={16} aria-hidden="true" />
                  Sair da conta
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
