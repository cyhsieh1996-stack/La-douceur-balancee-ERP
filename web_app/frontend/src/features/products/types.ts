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

export type UpdateProductResponse = CreateProductResponse;

export type DeleteProductResponse = {
  ok: true;
  source: "supabase";
};

export type RecipeRecord = {
  id: number;
  productId: number;
  materialId: number;
  materialName: string;
  unit: string | null;
  currentStock: number;
  qtyPerUnit: number;
  note: string | null;
};

export type RecipesResponse = {
  ok: true;
  items: RecipeRecord[];
  source: "supabase";
};

export type SaveRecipePayload = {
  materialId: number;
  qtyPerUnit: number;
  note?: string | null;
};

export type SaveRecipeResponse = {
  ok: true;
  item: RecipeRecord;
  source: "supabase";
};

export type DeleteRecipeResponse = {
  ok: true;
  source: "supabase";
};
