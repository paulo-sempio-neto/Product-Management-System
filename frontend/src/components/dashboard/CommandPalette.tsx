import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { CornerDownLeft, LogOut, PackagePlus, Pencil, Search } from "lucide-react";
import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { listProducts } from "../../api/products";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { useFocusTrap } from "../../hooks/useFocusTrap";
import { packagingColor } from "../../lib/packaging";
import type { Product } from "../../types/product";
import PriceTag from "../ui/PriceTag";

type Command = {
  id: string;
  group: "Ações" | "Produtos";
  label: string;
  icon: ReactNode;
  meta?: ReactNode;
  run: () => void;
};

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
  onCreate: () => void;
  onEdit: (product: Product) => void;
  onLogout: () => void;
};

function Palette({ onClose, onCreate, onEdit, onLogout }: Omit<CommandPaletteProps, "open">) {
  const panel = useRef<HTMLDivElement>(null);
  const listId = useId();
  const reduce = useReducedMotion();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [searching, setSearching] = useState(false);
  const [active, setActive] = useState(0);
  const term = useDebouncedValue(query.trim(), 180);
  useFocusTrap(panel, true, onClose);

  useEffect(() => {
    let ignore = false;
    setSearching(true);
    listProducts({ page: 1, limit: 6, name: term || undefined })
      .then((response) => !ignore && setResults(response.items))
      .catch(() => !ignore && setResults([]))
      .finally(() => !ignore && setSearching(false));
    return () => {
      ignore = true;
    };
  }, [term]);

  const commands = useMemo<Command[]>(() => {
    const actions = ([
      { id: "create", group: "Ações" as const, label: "Novo produto", icon: <PackagePlus size={18} />, meta: <kbd>N</kbd>, run: onCreate },
      { id: "logout", group: "Ações" as const, label: "Sair da conta", icon: <LogOut size={18} />, run: onLogout },
    ] satisfies Command[]).filter((action) => !query || action.label.toLowerCase().includes(query.trim().toLowerCase()));
    const products: Command[] = results.map((product) => ({
      id: `product-${product.id}`,
      group: "Produtos",
      label: product.name,
      icon: (
        <span className="palette__pack" style={{ background: packagingColor(product.name) }}>
          {product.name[0]?.toUpperCase()}
        </span>
      ),
      meta: <PriceTag value={product.price} />,
      run: () => onEdit(product),
    }));
    return [...actions, ...products];
  }, [query, results, onCreate, onEdit, onLogout]);

  useEffect(() => setActive(0), [query, results]);

  function execute(command: Command | undefined) {
    if (!command) return;
    onClose();
    // Let the palette unmount before opening another overlay.
    window.setTimeout(command.run, 60);
  }

  function onKeyDown(event: React.KeyboardEvent) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((index) => (index + 1) % Math.max(1, commands.length));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((index) => (index - 1 + commands.length) % Math.max(1, commands.length));
    } else if (event.key === "Enter") {
      event.preventDefault();
      execute(commands[active]);
    }
  }

  let lastGroup = "";

  return (
    <div className="overlay overlay--palette">
      <motion.div className="overlay__backdrop" onClick={onClose} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }} />
      <motion.div
        ref={panel}
        className="palette"
        role="dialog"
        aria-modal="true"
        aria-label="Buscar e executar comandos"
        initial={reduce ? { opacity: 0 } : { opacity: 0, scale: 0.97, y: -8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={reduce ? { opacity: 0 } : { opacity: 0, scale: 0.98, y: -6 }}
        transition={{ type: "spring", stiffness: 520, damping: 36 }}
      >
        <div className="palette__search">
          <Search size={20} aria-hidden="true" />
          <input
            data-autofocus
            role="combobox"
            aria-expanded="true"
            aria-controls={listId}
            aria-activedescendant={commands[active] ? `${listId}-${commands[active].id}` : undefined}
            placeholder="Busque um produto ou uma ação"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={onKeyDown}
          />
          {searching && <span className="palette__spinner" aria-hidden="true" />}
        </div>
        <ul id={listId} className="palette__list" role="listbox" aria-label="Resultados">
          {commands.length === 0 && !searching && <li className="palette__empty">Nada encontrado para “{query}”.</li>}
          {commands.map((command, index) => {
            const header = command.group !== lastGroup ? command.group : null;
            lastGroup = command.group;
            return (
              <li key={command.id} role="presentation">
                {header && (
                  <span className="palette__group" role="presentation">
                    {header}
                  </span>
                )}
                <div
                  id={`${listId}-${command.id}`}
                  role="option"
                  aria-selected={index === active}
                  className={`palette__item ${index === active ? "is-active" : ""}`}
                  onMouseMove={() => setActive(index)}
                  onClick={() => execute(command)}
                >
                  <span className="palette__icon">{command.icon}</span>
                  <span className="palette__label">{command.label}</span>
                  <span className="palette__meta">{command.meta}</span>
                  {command.group === "Produtos" && index === active && <Pencil size={15} className="palette__hint" aria-hidden="true" />}
                </div>
              </li>
            );
          })}
        </ul>
        <footer className="palette__footer" aria-hidden="true">
          <span>
            <kbd>↑</kbd>
            <kbd>↓</kbd> navegar
          </span>
          <span>
            <kbd>
              <CornerDownLeft size={12} />
            </kbd>{" "}
            abrir
          </span>
          <span>
            <kbd>Esc</kbd> fechar
          </span>
        </footer>
      </motion.div>
    </div>
  );
}

export default function CommandPalette({ open, ...props }: CommandPaletteProps) {
  return createPortal(<AnimatePresence>{open && <Palette {...props} />}</AnimatePresence>, document.body);
}
