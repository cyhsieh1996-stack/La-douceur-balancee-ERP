export type RawMaterial = {
  id: number;
  name: string;
  category: string | null;
  brand: string | null;
  vendor: string | null;
  unit: string | null;
  unitPrice: number;
  stock: number;
  safeStock: number;
};

export type MaterialsResponse = {
  items: RawMaterial[];
  source: "stub" | "supabase";
};

export type CreateMaterialPayload = {
  name: string;
  category?: string | null;
  brand?: string | null;
  vendor?: string | null;
  unit?: string | null;
  unitPrice?: number;
  stock?: number;
  safeStock?: number;
};

export type CreateMaterialResponse = {
  ok: true;
  item: RawMaterial;
  source: "supabase";
};
