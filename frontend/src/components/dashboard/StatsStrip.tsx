import { motion, useReducedMotion } from "motion/react";

import type { CatalogStats } from "../../hooks/useCatalog";
import { formatInteger, formatPrice } from "../../lib/format";
import AnimatedNumber from "../ui/AnimatedNumber";

export default function StatsStrip({ stats }: { stats: CatalogStats | null }) {
  const reduce = useReducedMotion();
  const peak = Math.max(1, ...(stats?.histogram ?? [1]));
  const partial = stats && stats.sampled < stats.total;

  return (
    <section className="stats" aria-label="Resumo do catálogo">
      <div className="stats__item">
        <span className="stats__label">Produtos no catálogo</span>
        <strong className="stats__value">
          {stats ? <AnimatedNumber value={stats.total} format={(v) => formatInteger(Math.round(v))} /> : <span className="skeleton skeleton--num" />}
        </strong>
      </div>
      <div className="stats__item">
        <span className="stats__label">Preço médio</span>
        <strong className="stats__value">
          {stats ? <AnimatedNumber value={stats.average} format={formatPrice} /> : <span className="skeleton skeleton--num" />}
        </strong>
      </div>
      <div className="stats__item stats__item--wide">
        <span className="stats__label">Distribuição de preços</span>
        {stats && stats.sampled > 0 ? (
          <>
            <div className="histogram" role="img" aria-label={`Preços entre ${formatPrice(stats.min)} e ${formatPrice(stats.max)}`}>
              {stats.histogram.map((count, index) => (
                <motion.span
                  key={index}
                  className={count === peak ? "is-peak" : ""}
                  initial={reduce ? false : { scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: 0.25 + index * 0.035, type: "spring", stiffness: 260, damping: 22 }}
                  style={{ height: `${Math.max(6, (count / peak) * 100)}%` }}
                />
              ))}
            </div>
            <div className="histogram__range tabular">
              <span>{formatPrice(stats.min)}</span>
              <span>{formatPrice(stats.max)}</span>
            </div>
          </>
        ) : (
          <p className="stats__empty">{stats ? "Aparece quando houver produtos." : <span className="skeleton skeleton--bar" />}</p>
        )}
      </div>
      {partial && <p className="stats__note">Médias calculadas com os primeiros {formatInteger(stats.sampled)} produtos.</p>}
    </section>
  );
}
