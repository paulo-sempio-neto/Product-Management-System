import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { PackagePlus, Pencil, SearchX, Trash2 } from "lucide-react";

import type { Product } from "../../types/product";
import Button from "../ui/Button";
import PriceTag from "../ui/PriceTag";
import { packagingColor } from "../../lib/packaging";


function initial(name: string) {
  return name.trim()[0]?.toUpperCase() ?? "?";
}

type ProductListProps = {
  products: Product[];
  loading: boolean;
  search: string;
  freshId: number | null;
  onEdit: (product: Product) => void;
  onDelete: (product: Product) => void;
  onCreate: () => void;
  onClearSearch: () => void;
};

export function ProductListSkeleton() {
  return (
    <ul className="plist" aria-hidden="true">
      {Array.from({ length: 6 }, (_, index) => (
        <li key={index} className="prow prow--skeleton">
          <span className="skeleton skeleton--avatar" />
          <span className="skeleton skeleton--line" style={{ width: `${40 + ((index * 17) % 35)}%` }} />
          <span className="skeleton skeleton--tag" />
        </li>
      ))}
    </ul>
  );
}

export default function ProductList({
  products,
  loading,
  search,
  freshId,
  onEdit,
  onDelete,
  onCreate,
  onClearSearch,
}: ProductListProps) {
  const reduce = useReducedMotion();

  if (!loading && products.length === 0) {
    return search ? (
      <div className="empty">
        <span className="empty__icon" aria-hidden="true">
          <SearchX size={26} />
        </span>
        <h3>Nenhum produto com “{search}”</h3>
        <p>Confira a grafia ou busque por parte do nome.</p>
        <Button variant="ghost" onClick={onClearSearch}>
          Limpar busca
        </Button>
      </div>
    ) : (
      <div className="empty">
        <div className="empty__shelf" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <h3>Sua prateleira está vazia</h3>
        <p>Cadastre o primeiro produto para começar a montar seu catálogo.</p>
        <Button icon={<PackagePlus size={18} />} onClick={onCreate}>
          Cadastrar primeiro produto
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="plist__head" aria-hidden="true">
        <span>Produto</span>
        <span>Preço</span>
        <span />
      </div>
      <motion.ul className={`plist ${loading ? "is-refreshing" : ""}`} aria-label="Produtos" layout={!reduce}>
        <AnimatePresence initial={false} mode="popLayout">
          {products.map((product, index) => (
            <motion.li
              key={product.id}
              layout={!reduce}
              className={`prow ${freshId === product.id ? "is-fresh" : ""}`}
              initial={reduce ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0, transition: { delay: Math.min(index, 10) * 0.025 } }}
              exit={reduce ? { opacity: 0 } : { opacity: 0, x: -24, transition: { duration: 0.2 } }}
              transition={{ type: "spring", stiffness: 500, damping: 40 }}
            >
              <span className="prow__pack" style={{ background: packagingColor(product.name) }} aria-hidden="true">
                {initial(product.name)}
              </span>
              <div className="prow__main">
                <span className="prow__name">{product.name}</span>
                <span className="prow__meta tabular">
                  Código {product.id}
                  {product.version > 1 && <span className="prow__edited">editado {product.version - 1}×</span>}
                </span>
              </div>
              <div className="prow__price">
                <span className="visually-hidden">Preço: </span>
                <PriceTag value={product.price} />
              </div>
              <div className="prow__actions">
                <button type="button" className="icon-btn" onClick={() => onEdit(product)} aria-label={`Editar ${product.name}`} title="Editar">
                  <Pencil size={17} />
                </button>
                <button
                  type="button"
                  className="icon-btn icon-btn--danger"
                  onClick={() => onDelete(product)}
                  aria-label={`Excluir ${product.name}`}
                  title="Excluir"
                >
                  <Trash2 size={17} />
                </button>
              </div>
            </motion.li>
          ))}
        </AnimatePresence>
      </motion.ul>
    </>
  );
}
