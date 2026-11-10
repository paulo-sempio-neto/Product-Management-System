import { priceParts } from "../../lib/format";

type PriceTagProps = { value: number; size?: "sm" | "lg" };

/** The yellow shelf price tag — the product's visual signature. */
export default function PriceTag({ value, size = "sm" }: PriceTagProps) {
  const { symbol, amount } = priceParts(value);
  const [whole, cents] = amount.split(",");
  return (
    <span className={`price-tag price-tag--${size}`}>
      <span className="price-tag__symbol">{symbol}</span>
      <span className="price-tag__whole">{whole}</span>
      {cents !== undefined && <span className="price-tag__cents">,{cents}</span>}
    </span>
  );
}
