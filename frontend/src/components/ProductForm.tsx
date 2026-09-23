import { type FormEvent, useState } from "react";

import type { ProductCreateInput } from "../types/product";

type ProductFormProps = {
  isSubmitting: boolean;
  errorMessage: string | null;
  successMessage: string | null;
  onSubmit: (input: ProductCreateInput) => Promise<boolean>;
};

const PRICE_PATTERN = /^\d+([.,]\d{1,2})?$/;

function normalizePrice(value: string): string {
  return value.trim().replace(",", ".");
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

export default function ProductForm({
  isSubmitting,
  errorMessage,
  successMessage,
  onSubmit,
}: ProductFormProps) {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validateProduct(name, price);
    if (validationError) {
      setValidationMessage(validationError);
      return;
    }

    setValidationMessage(null);

    const wasCreated = await onSubmit({
      name: name.trim(),
      price: normalizePrice(price),
    });

    if (wasCreated) {
      setName("");
      setPrice("");
    }
  }

  return (
    <form className="product-form" onSubmit={handleSubmit}>
      <div className="section-heading">
        <span className="section-kicker">Novo cadastro</span>
        <h2>Adicionar produto</h2>
        <p>Preencha os dados abaixo para incluir um item no catálogo.</p>
      </div>

      <div className="form-grid">
        <label className="field-group">
          <span className="field-label">Nome do produto</span>
          <input
            name="name"
            type="text"
            value={name}
            placeholder="Ex.: Arroz"
            disabled={isSubmitting}
            onChange={(event) => setName(event.target.value)}
          />
          <small>Use um nome curto e fácil de identificar.</small>
        </label>

        <label className="field-group">
          <span className="field-label">Preço</span>
          <input
            name="price"
            type="text"
            inputMode="decimal"
            value={price}
            placeholder="Ex.: 12.90"
            disabled={isSubmitting}
            onChange={(event) => setPrice(event.target.value)}
          />
          <small>Informe até duas casas decimais.</small>
        </label>

        <button
          type="submit"
          className={isSubmitting ? "is-loading" : undefined}
          disabled={isSubmitting}
        >
          {isSubmitting && <span className="button-spinner" aria-hidden="true" />}
          {isSubmitting ? "Salvando..." : "Criar produto"}
        </button>
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
