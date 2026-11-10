import { AnimatePresence, motion } from "motion/react";
import { RefreshCw } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { ApiRequestError, createProduct, getProduct, updateProduct } from "../../api/products";
import { normalizePriceInput, priceToInput, validatePriceInput } from "../../lib/format";
import type { Product } from "../../types/product";
import Button from "../ui/Button";
import Field from "../ui/Field";
import Overlay from "../ui/Overlay";
import PriceTag from "../ui/PriceTag";
import { isLightPackaging, packagingColor } from "../../lib/packaging";

type DrawerState = { mode: "create" } | { mode: "edit"; product: Product } | null;

type ProductDrawerProps = {
  state: DrawerState;
  onClose: () => void;
  onSaved: (product: Product, mode: "create" | "edit") => void;
};

export type { DrawerState };

export default function ProductDrawer({ state, onClose, onSaved }: ProductDrawerProps) {
  const editing = state?.mode === "edit" ? state.product : null;
  const [base, setBase] = useState<Product | null>(null);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [errors, setErrors] = useState<{ name?: string; price?: string; form?: string }>({});
  const [conflict, setConflict] = useState(false);
  const [saving, setSaving] = useState(false);
  const [reloading, setReloading] = useState(false);

  useEffect(() => {
    if (!state) return;
    setBase(editing);
    setName(editing?.name ?? "");
    setPrice(editing ? priceToInput(editing.price) : "");
    setErrors({});
    setConflict(false);
    setSaving(false);
  }, [state, editing]);

  const previewPrice = Number(normalizePriceInput(price));
  const priceIsValid = !validatePriceInput(price);
  const unchanged = base !== null && name.trim() === base.name && priceIsValid && previewPrice === base.price;

  async function reloadCurrent() {
    if (!base) return;
    setReloading(true);
    try {
      const fresh = await getProduct(base.id);
      setBase(fresh);
      setName(fresh.name);
      setPrice(priceToInput(fresh.price));
      setConflict(false);
      setErrors({});
    } catch {
      setErrors({ form: "Este produto não existe mais. Feche e atualize a lista." });
    } finally {
      setReloading(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const next = {
      name: name.trim() ? undefined : "Dê um nome ao produto.",
      price: validatePriceInput(price) ?? undefined,
    };
    setErrors(next);
    if (next.name || next.price) return;

    setSaving(true);
    setConflict(false);
    try {
      const input = { name: name.trim(), price: normalizePriceInput(price) };
      const saved = base ? await updateProduct(base.id, { ...input, version: base.version }) : await createProduct(input);
      onSaved(saved, base ? "edit" : "create");
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 409) {
        setConflict(true);
      } else if (error instanceof ApiRequestError && error.status === 404) {
        setErrors({ form: "Este produto foi excluído enquanto você editava." });
      } else {
        setErrors({ form: error instanceof Error ? error.message : "Não foi possível salvar. Tente de novo." });
      }
      setSaving(false);
    }
  }

  const title = base ? "Editar produto" : "Novo produto";

  return (
    <Overlay
      variant="drawer"
      open={state !== null}
      onClose={onClose}
      title={title}
      description={base ? `Código ${base.id}` : "Ele aparece no catálogo assim que você salvar."}
      footer={
        <>
          <Button type="button" variant="quiet" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" form="product-form" loading={saving} disabled={unchanged || conflict}>
            {base ? "Salvar alterações" : "Salvar produto"}
          </Button>
        </>
      }
    >
      <div className="preview" aria-hidden="true">
        <div className="preview__shelf">
          <motion.div
            className="preview__pack"
            key={name.trim()[0] ?? "empty"}
            style={name.trim() ? { background: packagingColor(name), color: isLightPackaging(packagingColor(name)) ? "var(--tag-ink)" : "#fff" } : undefined}
            initial={{ y: -14, opacity: 0.4 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness: 520, damping: 16 }}
          >
            {name.trim()[0]?.toUpperCase() ?? "?"}
          </motion.div>
          <span className="preview__name">{name.trim() || "Nome do produto"}</span>
        </div>
        <div className="preview__tag">{priceIsValid ? <PriceTag value={previewPrice} size="lg" /> : <span className="preview__tag-empty">R$ —</span>}</div>
      </div>

      <form id="product-form" className="pform" onSubmit={handleSubmit} noValidate>
        <Field
          label="Nome do produto"
          data-autofocus
          placeholder="Ex.: Arroz integral 5kg"
          value={name}
          maxLength={120}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          hint="Use o nome que aparece na embalagem."
        />
        <Field
          label="Preço"
          inputMode="decimal"
          placeholder="0,00"
          icon={<span className="pform__currency">R$</span>}
          value={price}
          onChange={(e) => setPrice(e.target.value.replace(/[^\d.,]/g, ""))}
          onBlur={() => price && setErrors((current) => ({ ...current, price: validatePriceInput(price) ?? undefined }))}
          error={errors.price}
          hint="Use vírgula para os centavos, como 12,90."
        />

        <AnimatePresence>
          {conflict && (
            <motion.div className="notice notice--warn" role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
              <p>
                <strong>Alguém alterou este produto antes de você.</strong> Carregue a versão atual e refaça sua mudança para não sobrescrever o trabalho de outra pessoa.
              </p>
              <Button type="button" variant="ghost" size="sm" icon={<RefreshCw size={15} />} loading={reloading} onClick={reloadCurrent}>
                Carregar versão atual
              </Button>
            </motion.div>
          )}
          {errors.form && (
            <motion.p className="notice notice--error" role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
              {errors.form}
            </motion.p>
          )}
        </AnimatePresence>
      </form>
    </Overlay>
  );
}
