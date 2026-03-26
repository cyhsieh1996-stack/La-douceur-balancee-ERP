import { createSupabaseAdmin } from "./supabase";

type InboundEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

type InboundPayload = {
  materialId?: number;
  qty?: number;
  unitPrice?: number;
  batchNumber?: string | null;
  expiryDate?: string | null;
  note?: string | null;
};

function mapInboundRow(row: Record<string, unknown>) {
  const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
  return {
    id: Number(row.id),
    date: String(row.created_at ?? ""),
    materialId: material?.id ? Number(material.id) : null,
    materialName: material?.name ? String(material.name) : "-",
    unit: material?.unit ? String(material.unit) : null,
    qty: Number(row.qty ?? 0),
    unitPrice: Number(row.unit_price ?? 0),
    batchNumber: row.batch_number ? String(row.batch_number) : null,
    expiryDate: row.expiry_date ? String(row.expiry_date) : null,
    note: row.note ? String(row.note) : null,
  };
}

export async function listInboundRecords(env: InboundEnv, limit = 20) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("inbound_records")
    .select("id, qty, unit_price, batch_number, expiry_date, note, created_at, raw_materials(id, name, unit)")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapInboundRow(row)),
  };
}

export async function createInboundRecord(env: InboundEnv, payload: InboundPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const materialId = Number(payload.materialId);
  const qty = Number(payload.qty);
  const unitPrice = Number(payload.unitPrice ?? 0);
  const batchNumber = (payload.batchNumber ?? "").trim() || null;
  const expiryDate = (payload.expiryDate ?? "").trim() || null;
  const note = (payload.note ?? "").trim() || null;

  if (!Number.isFinite(materialId)) {
    return { ok: false as const, error: "原料編號無效" };
  }

  if (!Number.isFinite(qty) || qty <= 0) {
    return { ok: false as const, error: "入庫數量必須大於 0" };
  }

  if (!Number.isFinite(unitPrice) || unitPrice < 0) {
    return { ok: false as const, error: "進貨單價不得小於 0" };
  }

  const materialResult = await supabase
    .from("raw_materials")
    .select("id, stock, unit_price")
    .eq("id", materialId)
    .maybeSingle();

  if (materialResult.error) {
    return { ok: false as const, error: materialResult.error.message };
  }

  if (!materialResult.data) {
    return { ok: false as const, error: "找不到該原料" };
  }

  const insertResult = await supabase
    .from("inbound_records")
    .insert({
      material_id: materialId,
      qty,
      unit_price: unitPrice,
      batch_number: batchNumber,
      expiry_date: expiryDate,
      note,
    })
    .select("id, qty, unit_price, batch_number, expiry_date, note, created_at, raw_materials(id, name, unit)")
    .single();

  if (insertResult.error) {
    return { ok: false as const, error: insertResult.error.message };
  }

  const nextStock = Number(materialResult.data.stock ?? 0) + qty;
  const nextUnitPrice = unitPrice > 0 ? unitPrice : Number(materialResult.data.unit_price ?? 0);

  const updateResult = await supabase
    .from("raw_materials")
    .update({
      stock: nextStock,
      unit_price: nextUnitPrice,
    })
    .eq("id", materialId)
    .select("id, name, unit, stock, unit_price")
    .single();

  if (updateResult.error) {
    return { ok: false as const, error: updateResult.error.message };
  }

  return {
    ok: true as const,
    item: mapInboundRow(insertResult.data),
    material: {
      id: Number(updateResult.data.id),
      name: String(updateResult.data.name ?? ""),
      unit: updateResult.data.unit ? String(updateResult.data.unit) : null,
      stock: Number(updateResult.data.stock ?? 0),
      unitPrice: Number(updateResult.data.unit_price ?? 0),
    },
  };
}
