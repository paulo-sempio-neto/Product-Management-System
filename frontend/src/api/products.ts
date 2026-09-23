import type {
  Product,
  ProductCreateInput,
  ProductListResponse,
  ProductUpdateInput,
} from "../types/product";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

type ListProductsParams = {
  page?: number;
  limit?: number;
  name?: string;
};

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function listProducts(
  params: ListProductsParams = {},
): Promise<ProductListResponse> {
  const query = new URLSearchParams();

  if (params.page !== undefined) {
    query.set("page", String(params.page));
  }

  if (params.limit !== undefined) {
    query.set("limit", String(params.limit));
  }

  if (params.name?.trim()) {
    query.set("name", params.name.trim());
  }

  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return request<ProductListResponse>(`/products${suffix}`);
}

export function createProduct(input: ProductCreateInput): Promise<Product> {
  return request<Product>("/products", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateProduct(
  productId: number,
  input: ProductUpdateInput,
): Promise<Product> {
  return request<Product>(`/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function deleteProduct(productId: number): Promise<void> {
  return request<void>(`/products/${productId}`, {
    method: "DELETE",
  });
}
