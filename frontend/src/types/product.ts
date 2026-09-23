export type Product = {
  id: number;
  name: string;
  price: number;
  version: number;
};

export type ProductListResponse = {
  items: Product[];
  page: number;
  limit: number;
  total: number;
};

export type ProductCreateInput = {
  name: string;
  price: string;
};

export type ProductUpdateInput = ProductCreateInput & {
  version: number;
};
