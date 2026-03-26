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

type ProductPayload = {
  name?: string;
  category?: string | null;
  price?: number;
  cost?: number;
  stock?: number;
  shelfLife?: number | null;
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

export async function createProduct(env: ProductEnv, payload: ProductPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const name = (payload.name ?? "").trim();
  if (!name) {
    return { ok: false as const, error: "產品名稱不可空白" };
  }

  const { data, error } = await supabase
    .from("products")
    .insert({
      name,
      category: payload.category ?? null,
      price: payload.price ?? 0,
      cost: payload.cost ?? 0,
      stock: payload.stock ?? 0,
      shelf_life: payload.shelfLife ?? null,
    })
    .select("id, name, category, price, cost, stock, shelf_life")
    .single();

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    item: mapProductRow(data),
  };
}
