import { type FormEvent, useEffect, useState } from "react";

import type { Product, ProductUpdateInput } from "../types/product";

type ProductEditFormProps = {
  product: Product;
  isSubmitting: boolean;
  errorMessage: string | null;
  successMessage: string | null;
  onCancel: () => void;
  onSubmit: (input: ProductUpdateInput) => Promise<boolean>;
};

const PRICE_PATTERN = /^\d+([.,]\d{1,2})?$/;

function normalizePrice(value: string): string {
  return value.trim().replace(",", ".");
}

function formatPriceForInput(value: number): string {
  return value.toFixed(2);
}

function validateProduct(name: string, price: string): string | null {
  if (!name.trim()) {
    return "Informe o nome do produto.";
  }

  const normalizedPrice = normalizePrice(price);

  if (!normalizedPrice) {
    return "Informe o preço do produto.";
  }

  if (!PRICE_PATTERN.test(price.trim())) {
    return "Informe um preço positivo com no máximo duas casas decimais.";
  }

  if (Number(normalizedPrice) <= 0) {
    return "O preço deve ser maior que zero.";
  }

  return null;
}

export default function ProductEditForm({
  product,
  isSubmitting,
  errorMessage,
  successMessage,
  onCancel,
  onSubmit,
}: ProductEditFormProps) {
  const [name, setName] = useState(product.name);
  const [price, setPrice] = useState(formatPriceForInput(product.price));
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  useEffect(() => {
    setName(product.name);
    setPrice(formatPriceForInput(product.price));
    setValidationMessage(null);
  }, [product]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validateProduct(name, price);
    if (validationError) {
      setValidationMessage(validationError);
      return;
    }

    setValidationMessage(null);

    await onSubmit({
      name: name.trim(),
      price: normalizePrice(price),
      version: product.version,
    });
  }

  return (
    <form className="product-form" onSubmit={handleSubmit}>
      <div className="section-heading">
        <span className="section-kicker">Edição em andamento</span>
        <h2>Editar produto</h2>
        <p>
          Produto #{product.id} · versão {product.version}. O controle de versão
          protege o registro contra alterações simultâneas.
        </p>
      </div>

      <div className="form-grid">
        <label className="field-group">
          <span className="field-label">Nome do produto</span>
          <input
            name="edit-name"
            type="text"
            value={name}
            disabled={isSubmitting}
            onChange={(event) => setName(event.target.value)}
          />
          <small>Atualize o nome de exibição do item.</small>
        </label>

        <label className="field-group">
          <span className="field-label">Preço</span>
          <input
            name="edit-price"
            type="text"
            inputMode="decimal"
            value={price}
            disabled={isSubmitting}
            onChange={(event) => setPrice(event.target.value)}
          />
          <small>Informe até duas casas decimais.</small>
        </label>

        <div className="form-actions">
          <button
            type="submit"
            className={isSubmitting ? "is-loading" : undefined}
            disabled={isSubmitting}
          >
            {isSubmitting && (
              <span className="button-spinner" aria-hidden="true" />
            )}
            {isSubmitting ? "Salvando..." : "Salvar edição"}
          </button>
          <button
            type="button"
            className="secondary"
            disabled={isSubmitting}
            onClick={onCancel}
          >
            Cancelar
          </button>
        </div>
      </div>

      {validationMessage && (
        <p className="form-message error" role="alert">
          {validationMessage}
        </p>
      )}

      {errorMessage && !validationMessage && (
        <p className="form-message error" role="alert">
          {errorMessage}
        </p>
      )}

      {successMessage && !errorMessage && !validationMessage && (
        <p className="form-message success" role="status">
          {successMessage}
        </p>
      )}
    </form>
  );
}
