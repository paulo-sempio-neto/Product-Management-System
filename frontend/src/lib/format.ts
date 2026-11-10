const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const integer = new Intl.NumberFormat("pt-BR");

export const formatPrice = (value: number) => currency.format(value);
export const formatInteger = (value: number) => integer.format(value);

/** Splits "R$ 12,90" into currency symbol and amount for typographic control. */
export function priceParts(value: number) {
  const parts = currency.formatToParts(value);
  const symbol = parts.find((p) => p.type === "currency")?.value ?? "R$";
  const amount = parts
    .filter((p) => p.type !== "currency" && p.type !== "literal")
    .map((p) => p.value)
    .join("");
  return { symbol, amount };
}

/** Accepts "12,90", "12.90", "1.234,56" and returns the API format "1234.56". */
export function normalizePriceInput(raw: string): string {
  const cleaned = raw.trim().replace(/[^\d.,]/g, "");
  if (!cleaned) return "";
  const decimalIndex = Math.max(cleaned.lastIndexOf(","), cleaned.lastIndexOf("."));
  if (decimalIndex === -1) return cleaned;
  const separator = cleaned[decimalIndex];
  const hasBoth = cleaned.includes(",") && cleaned.includes(".");
  const repeated = cleaned.split(separator).length > 2;
  // "1.234.567" (same separator repeated, no other) is grouping only.
  if (repeated && !hasBoth) return cleaned.replace(/[.,]/g, "");
  const whole = cleaned.slice(0, decimalIndex).replace(/[.,]/g, "");
  return `${whole || "0"}.${cleaned.slice(decimalIndex + 1)}`;
}

export function validatePriceInput(raw: string): string | null {
  const normalized = normalizePriceInput(raw);
  if (!normalized) return "Informe o preço.";
  if (!/^\d+(\.\d{1,2})?$/.test(normalized)) return "Use no máximo duas casas decimais, como 12,90.";
  if (Number(normalized) <= 0) return "O preço precisa ser maior que zero.";
  return null;
}

/** Formats a stored number for editing in a pt-BR input: 12.9 → "12,90". */
export const priceToInput = (value: number) => value.toFixed(2).replace(".", ",");
