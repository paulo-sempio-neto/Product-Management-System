const PACKAGING = ["#ffd23f", "#ff5a5f", "#12b886", "#2b4bff", "#0e1530", "#8b5cf6"];

/** Stable "packaging" color per product name, shared by list and preview. */
export function packagingColor(name: string) {
  let hash = 0;
  for (const char of name.trim()) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return PACKAGING[hash % PACKAGING.length];
}

export const isLightPackaging = (color: string) => color === "#ffd23f";
