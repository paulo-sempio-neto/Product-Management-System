import type {
  Product,
  ProductCreateInput,
  ProductListResponse,
  ProductUpdateInput,
} from "../types/product";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export type ListProductsParams = {
  page?: number;
  limit?: number;
  name?: string;
};

type ApiErrorResponse = {
  detail?: string | Array<{ msg: string }>;
  error?: {
    code: string;
  };
};

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

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
    let message = `API request failed with status ${response.status}`;
    let code: string | undefined;

    try {
      const errorBody = (await response.json()) as ApiErrorResponse;
      code = errorBody.error?.code;

      if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      } else if (Array.isArray(errorBody.detail) && errorBody.detail[0]?.msg) {
        message = errorBody.detail[0].msg;
      }
    } catch {
      // Keep the generic status-based message when the response body is empty
      // or not JSON.
    }

    throw new ApiRequestError(message, response.status, code);
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
