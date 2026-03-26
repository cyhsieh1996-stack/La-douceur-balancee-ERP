import { createSupabaseAdmin } from "./supabase";

type RecipeEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

type RecipePayload = {
  materialId?: number;
  qtyPerUnit?: number;
  note?: string | null;
};

function mapRecipeRow(row: Record<string, unknown>) {
  const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
  return {
    id: Number(row.id),
    productId: Number(row.product_id),
    materialId: Number(row.material_id),
    materialName: material?.name ? String(material.name) : "",
    unit: material?.unit ? String(material.unit) : null,
    currentStock:
      material?.stock === null || material?.stock === undefined ? 0 : Number(material.stock),
    qtyPerUnit: Number(row.qty_per_unit ?? 0),
    note: row.note ? String(row.note) : null,
  };
}

export async function listRecipes(env: RecipeEnv, productId: number) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("product_recipes")
    .select("id, product_id, material_id, qty_per_unit, note, raw_materials(name, unit, stock)")
    .eq("product_id", productId)
    .order("material_id", { ascending: true });

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapRecipeRow(row)),
  };
}

export async function saveRecipe(env: RecipeEnv, productId: number, payload: RecipePayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const materialId = Number(payload.materialId);
  const qtyPerUnit = Number(payload.qtyPerUnit);
  const note = (payload.note ?? "").trim() || null;

  if (!Number.isFinite(materialId)) {
    return { ok: false as const, error: "原料編號無效" };
  }

  if (!Number.isFinite(qtyPerUnit) || qtyPerUnit <= 0) {
    return { ok: false as const, error: "每單位用量必須大於 0" };
  }

  const { data, error } = await supabase
    .from("product_recipes")
    .upsert(
      {
        product_id: productId,
        material_id: materialId,
        qty_per_unit: qtyPerUnit,
        note,
      },
      { onConflict: "product_id,material_id" },
    )
    .select("id, product_id, material_id, qty_per_unit, note, raw_materials(name, unit, stock)")
    .single();

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    item: mapRecipeRow(data),
  };
}

export async function deleteRecipe(env: RecipeEnv, recipeId: number) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase.from("product_recipes").delete().eq("id", recipeId).select("id").maybeSingle();

  if (error) {
    return { ok: false as const, error: error.message };
  }

  if (!data) {
    return { ok: false as const, error: "Recipe not found" };
  }

  return { ok: true as const };
}
