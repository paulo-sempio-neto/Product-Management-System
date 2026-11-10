import { ChevronLeft, ChevronRight } from "lucide-react";

import { formatInteger } from "../../lib/format";

type PaginationBarProps = {
  page: number;
  limit: number;
  total: number;
  disabled: boolean;
  onChange: (page: number) => void;
};

function pageWindow(current: number, last: number): Array<number | "gap"> {
  const pages = new Set([1, last, current - 1, current, current + 1]);
  const sorted = [...pages].filter((p) => p >= 1 && p <= last).sort((a, b) => a - b);
  const result: Array<number | "gap"> = [];
  sorted.forEach((p, index) => {
    if (index > 0 && p - sorted[index - 1] > 1) result.push("gap");
    result.push(p);
  });
  return result;
}

export default function PaginationBar({ page, limit, total, disabled, onChange }: PaginationBarProps) {
  const last = Math.max(1, Math.ceil(total / limit));
  const from = total === 0 ? 0 : (page - 1) * limit + 1;
  const to = Math.min(page * limit, total);
  if (total === 0) return null;

  return (
    <nav className="pager" aria-label="Paginação">
      <p className="pager__summary tabular">
        {formatInteger(from)}–{formatInteger(to)} de {formatInteger(total)}
      </p>
      {last > 1 && (
        <div className="pager__controls">
          <button type="button" className="icon-btn" disabled={disabled || page <= 1} onClick={() => onChange(page - 1)} aria-label="Página anterior">
            <ChevronLeft size={18} />
          </button>
          {pageWindow(page, last).map((item, index) =>
            item === "gap" ? (
              <span key={`gap-${index}`} className="pager__gap" aria-hidden="true">
                …
              </span>
            ) : (
              <button
                key={item}
                type="button"
                className={`pager__page tabular ${item === page ? "is-current" : ""}`}
                aria-current={item === page ? "page" : undefined}
                aria-label={`Página ${item}`}
                disabled={disabled}
                onClick={() => onChange(item)}
              >
                {item}
              </button>
            ),
          )}
          <button type="button" className="icon-btn" disabled={disabled || page >= last} onClick={() => onChange(page + 1)} aria-label="Próxima página">
            <ChevronRight size={18} />
          </button>
        </div>
      )}
    </nav>
  );
}
