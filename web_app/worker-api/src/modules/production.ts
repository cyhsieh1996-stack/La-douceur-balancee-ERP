import { createSupabaseAdmin } from "./supabase";

type ProductionEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

type ProductionPayload = {
  productId?: number;
  qty?: number;
  batchNumber?: string | null;
  expiryDate?: string | null;
  note?: string | null;
};

function encodeBatchCode(dateObj: Date, productId: number, seq: number) {
  const baseYear = 2025;
  const yearChar = String.fromCharCode("A".charCodeAt(0) + (dateObj.getFullYear() - baseYear));
  const month = dateObj.getMonth() + 1;
  const monthChar = month < 10 ? String(month) : ({ 10: "A", 11: "B", 12: "C" }[month] ?? "X");
  const dayStr = String(dateObj.getDate()).padStart(2, "0");
  const obfuscatedId = (productId * 17 + 99).toString(16).toUpperCase();
  return `${yearChar}${monthChar}${dayStr}-${obfuscatedId}-${String(seq).padStart(2, "0")}`;
}

function mapProductionRow(row: Record<string, unknown>) {
  const product = Array.isArray(row.products) ? row.products[0] : row.products;
  return {
    id: Number(row.id),
    productId: product?.id ? Number(product.id) : null,
    productName: product?.name ? String(product.name) : "-",
    qty: Number(row.qty ?? 0),
    batchNumber: row.batch_number ? String(row.batch_number) : null,
    expiryDate: row.expiry_date ? String(row.expiry_date) : null,
    note: row.note ? String(row.note) : null,
    date: String(row.created_at ?? ""),
  };
}

export async function listProductionLogs(env: ProductionEnv, limit = 20) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("production_logs")
    .select("id, qty, batch_number, expiry_date, note, created_at, products(id, name)")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapProductionRow(row)),
  };
}

export async function generateBatchNumber(env: ProductionEnv, productId: number) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const now = new Date();
  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const end = new Date(now);
  end.setHours(23, 59, 59, 999);

  const { count, error } = await supabase
    .from("production_logs")
    .select("*", { count: "exact", head: true })
    .eq("product_id", productId)
    .gte("created_at", start.toISOString())
    .lte("created_at", end.toISOString());

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    batchNumber: encodeBatchCode(now, productId, (count ?? 0) + 1),
  };
}

export async function getProductionPreview(env: ProductionEnv, productId: number, qty: number) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("product_recipes")
    .select("id, material_id, qty_per_unit, note, raw_materials(name, unit, stock)")
    .eq("product_id", productId)
    .order("material_id", { ascending: true });

  if (error) {
    return { ok: false as const, error: error.message };
  }

  const items = (data ?? []).map((row) => {
    const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
    const currentStock = Number(material?.stock ?? 0);
    const qtyPerUnit = Number(row.qty_per_unit ?? 0);
    const requiredQty = qtyPerUnit * qty;
    return {
      id: Number(row.id),
      materialId: Number(row.material_id),
      materialName: material?.name ? String(material.name) : "-",
      unit: material?.unit ? String(material.unit) : null,
      currentStock,
      qtyPerUnit,
      requiredQty,
      remainingStock: currentStock - requiredQty,
      note: row.note ? String(row.note) : null,
      isShortage: requiredQty > currentStock,
    };
  });

  return {
    ok: true as const,
    items,
    shortages: items.filter((item) => item.isShortage),
  };
}

export async function createProductionLog(env: ProductionEnv, payload: ProductionPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const productId = Number(payload.productId);
  const qty = Number(payload.qty);
  const batchNumber = (payload.batchNumber ?? "").trim() || null;
  const expiryDate = (payload.expiryDate ?? "").trim() || null;
  const note = (payload.note ?? "").trim() || null;

  if (!Number.isFinite(productId)) {
    return { ok: false as const, error: "產品編號無效" };
  }

  if (!Number.isFinite(qty) || qty <= 0) {
    return { ok: false as const, error: "生產數量必須大於 0" };
  }

  const productResult = await supabase.from("products").select("id, name, stock").eq("id", productId).maybeSingle();
  if (productResult.error) {
    return { ok: false as const, error: productResult.error.message };
  }
  if (!productResult.data) {
    return { ok: false as const, error: "找不到產品" };
  }

  const preview = await getProductionPreview(env, productId, qty);
  if (!preview.ok) {
    return preview;
  }

  if (preview.shortages.length > 0) {
    const lines = preview.shortages.map(
      (row) => `${row.materialName} 需要 ${row.requiredQty}${row.unit ?? ""}，現有 ${row.currentStock}${row.unit ?? ""}`,
    );
    return { ok: false as const, error: `原料不足，無法生產：\n${lines.join("\n")}` };
  }

  const insertResult = await supabase
    .from("production_logs")
    .insert({
      product_id: productId,
      qty,
      batch_number: batchNumber,
      expiry_date: expiryDate,
      note,
    })
    .select("id, qty, batch_number, expiry_date, note, created_at, products(id, name)")
    .single();

  if (insertResult.error) {
    return { ok: false as const, error: insertResult.error.message };
  }

  const updateProductResult = await supabase
    .from("products")
    .update({ stock: Number(productResult.data.stock ?? 0) + qty })
    .eq("id", productId);

  if (updateProductResult.error) {
    return { ok: false as const, error: updateProductResult.error.message };
  }

  for (const row of preview.items) {
    const updateMaterialResult = await supabase
      .from("raw_materials")
      .update({ stock: row.remainingStock })
      .eq("id", row.materialId);

    if (updateMaterialResult.error) {
      return { ok: false as const, error: updateMaterialResult.error.message };
    }
  }

  return {
    ok: true as const,
    item: mapProductionRow(insertResult.data),
    recipePreview: preview.items,
  };
}
