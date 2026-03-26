import { createSupabaseAdmin } from "./supabase";

export type ProductRecord = {
  id: number;
  name: string;
  category: string | null;
  price: number;
  cost: number;
  stock: number;
  shelfLife: number | null;
};

type ProductEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

function mapProductRow(row: Record<string, unknown>): ProductRecord {
  return {
    id: Number(row.id),
    name: String(row.name ?? ""),
    category: row.category ? String(row.category) : null,
    price: Number(row.price ?? 0),
    cost: Number(row.cost ?? 0),
    stock: Number(row.stock ?? 0),
    shelfLife: row.shelf_life === null || row.shelf_life === undefined ? null : Number(row.shelf_life),
  };
}

export async function listProducts(env: ProductEnv) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("products")
    .select("id, name, category, price, cost, stock, shelf_life")
    .order("name", { ascending: true });

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapProductRow(row)),
  };
}
