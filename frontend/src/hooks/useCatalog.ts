import { useCallback, useEffect, useState } from "react";

import { listProducts } from "../api/products";
import type { Product, ProductListResponse } from "../types/product";

export const PAGE_SIZE = 12;
const STATS_PAGE = 100; // API maximum per request
const STATS_MAX_PAGES = 10;

export type CatalogStats = {
  total: number;
  sampled: number;
  average: number;
  min: number;
  max: number;
  histogram: number[];
};

const EMPTY_PAGE: ProductListResponse = { items: [], page: 1, limit: PAGE_SIZE, total: 0 };

function buildStats(products: Product[], total: number): CatalogStats {
  if (products.length === 0) return { total, sampled: 0, average: 0, min: 0, max: 0, histogram: [] };
  const prices = products.map((p) => p.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const buckets = 14;
  const histogram = new Array<number>(buckets).fill(0);
  const span = max - min || 1;
  prices.forEach((price) => {
    histogram[Math.min(buckets - 1, Math.floor(((price - min) / span) * buckets))]++;
  });
  return {
    total,
    sampled: products.length,
    average: prices.reduce((sum, price) => sum + price, 0) / prices.length,
    min,
    max,
    histogram,
  };
}

/** Loads the current page of products plus catalog-wide price stats. */
export function useCatalog(page: number, search: string) {
  const [data, setData] = useState<ProductListResponse>(EMPTY_PAGE);
  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);

  const refresh = useCallback(() => setVersion((value) => value + 1), []);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError(null);
    listProducts({ page, limit: PAGE_SIZE, name: search || undefined })
      .then((result) => {
        if (!ignore) setData(result);
      })
      .catch((reason: unknown) => {
        if (!ignore) setError(reason instanceof Error ? reason.message : "Erro desconhecido.");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [page, search, version]);

  useEffect(() => {
    let ignore = false;
    async function loadStats() {
      const first = await listProducts({ page: 1, limit: STATS_PAGE });
      const pages = Math.min(Math.ceil(first.total / STATS_PAGE), STATS_MAX_PAGES);
      const rest = await Promise.all(
        Array.from({ length: Math.max(0, pages - 1) }, (_, index) => listProducts({ page: index + 2, limit: STATS_PAGE })),
      );
      const all = [first, ...rest].flatMap((result) => result.items);
      if (!ignore) setStats(buildStats(all, first.total));
    }
    loadStats().catch(() => {
      if (!ignore) setStats(null);
    });
    return () => {
      ignore = true;
    };
  }, [version]);

  return { data, stats, loading, error, refresh };
}
