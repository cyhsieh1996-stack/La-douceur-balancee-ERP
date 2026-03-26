export type ProductRecord = {
  id: number;
  name: string;
  category: string | null;
  price: number;
  cost: number;
  stock: number;
  shelfLife: number | null;
};

export type ProductsResponse = {
  items: ProductRecord[];
  source: "stub" | "supabase";
};

export type CreateProductPayload = {
  name: string;
  category?: string | null;
  price?: number;
  cost?: number;
  stock?: number;
  shelfLife?: number | null;
};

export type CreateProductResponse = {
  ok: true;
  item: ProductRecord;
  source: "supabase";
};
