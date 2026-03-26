import { createSupabaseAdmin } from "./supabase";

export type MaterialRecord = {
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

type MaterialPayload = {
  name?: string;
  category?: string | null;
  brand?: string | null;
  vendor?: string | null;
  unit?: string | null;
  unitPrice?: number;
  stock?: number;
  safeStock?: number;
};

type MaterialEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

function mapMaterialRow(row: Record<string, unknown>): MaterialRecord {
  return {
    id: Number(row.id),
    name: String(row.name ?? ""),
    category: row.category ? String(row.category) : null,
    brand: row.brand ? String(row.brand) : null,
    vendor: row.vendor ? String(row.vendor) : null,
    unit: row.unit ? String(row.unit) : null,
    unitPrice: Number(row.unit_price ?? 0),
    stock: Number(row.stock ?? 0),
    safeStock: Number(row.safe_stock ?? 0),
  };
}

export async function listMaterials(env: MaterialEnv) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return {
      ok: false as const,
      error: "Supabase admin client is not configured.",
    };
  }

  const { data, error } = await supabase
    .from("raw_materials")
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .order("name", { ascending: true });

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapMaterialRow(row)),
  };
}

export async function getMaterialById(env: MaterialEnv, id: number) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return {
      ok: false as const,
      error: "Supabase admin client is not configured.",
    };
  }

  const { data, error } = await supabase
    .from("raw_materials")
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .eq("id", id)
    .maybeSingle();

  if (error) {
    return { ok: false as const, error: error.message };
  }

  if (!data) {
    return { ok: false as const, error: "Material not found" };
  }

  return {
    ok: true as const,
    item: mapMaterialRow(data),
  };
}

export async function createMaterial(env: MaterialEnv, payload: MaterialPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return {
      ok: false as const,
      error: "Supabase admin client is not configured.",
    };
  }

  const name = (payload.name ?? "").trim();
  if (!name) {
    return { ok: false as const, error: "名稱不可空白" };
  }

  const { data, error } = await supabase
    .from("raw_materials")
    .insert({
      name,
      category: payload.category ?? null,
      brand: payload.brand ?? null,
      vendor: payload.vendor ?? null,
      unit: payload.unit ?? null,
      unit_price: payload.unitPrice ?? 0,
      stock: payload.stock ?? 0,
      safe_stock: payload.safeStock ?? 50,
    })
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .single();

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    item: mapMaterialRow(data),
  };
}
