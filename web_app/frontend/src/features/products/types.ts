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
