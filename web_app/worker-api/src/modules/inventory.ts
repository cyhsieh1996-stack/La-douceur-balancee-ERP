import { createSupabaseAdmin } from "./supabase";

type InventoryEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

type InventoryFilters = {
  keyword?: string;
  lowStockOnly?: boolean;
  limit?: number;
};

type InventoryAdjustmentPayload = {
  materialId?: number;
  newStock?: number;
  reason?: string | null;
};

type MaterialRow = {
  id: number;
  name: string;
  category: string | null;
  brand: string | null;
  vendor: string | null;
  unit: string | null;
  unit_price: number;
  stock: number;
  safe_stock: number;
};

function mapMaterialRow(row: Record<string, unknown>): MaterialRow {
  return {
    id: Number(row.id),
    name: String(row.name ?? ""),
    category: row.category ? String(row.category) : null,
    brand: row.brand ? String(row.brand) : null,
    vendor: row.vendor ? String(row.vendor) : null,
    unit: row.unit ? String(row.unit) : null,
    unit_price: Number(row.unit_price ?? 0),
    stock: Number(row.stock ?? 0),
    safe_stock: Number(row.safe_stock ?? 0),
  };
}

function matchesKeyword(row: MaterialRow, keyword: string) {
  const value = keyword.trim().toLowerCase();
  if (!value) return true;
  return [row.name, row.category, row.brand, row.vendor].some((field) => (field ?? "").toLowerCase().includes(value));
}

function isLowStock(row: MaterialRow) {
  return row.safe_stock > 0 && row.stock < row.safe_stock;
}

export async function getInventoryCenter(env: InventoryEnv, filters: InventoryFilters = {}) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const materialsQuery = supabase
    .from("raw_materials")
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .order("name", { ascending: true });

  const adjustmentsQuery = supabase
    .from("inventory_adjustments")
    .select("id, old_stock, new_stock, diff, reason, created_at, raw_materials(id, name, unit)")
    .order("created_at", { ascending: false })
    .limit(filters.limit ?? 20);

  const [materialsResult, adjustmentsResult] = await Promise.all([materialsQuery, adjustmentsQuery]);

  if (materialsResult.error) {
    return { ok: false as const, error: materialsResult.error.message };
  }

  if (adjustmentsResult.error) {
    return { ok: false as const, error: adjustmentsResult.error.message };
  }

  const materials = (materialsResult.data ?? []).map((row) => mapMaterialRow(row));
  const filteredMaterials = materials
    .filter((row) => matchesKeyword(row, filters.keyword ?? ""))
    .filter((row) => (filters.lowStockOnly ? isLowStock(row) : true))
    .map((row) => ({
      id: row.id,
      name: row.name,
      category: row.category,
      brand: row.brand,
      vendor: row.vendor,
      unit: row.unit,
      unitPrice: row.unit_price,
      stock: row.stock,
      safeStock: row.safe_stock,
      balanceToSafe: row.stock - row.safe_stock,
      isLowStock: isLowStock(row),
    }));

  const summary = {
    materialCount: materials.length,
    lowStockCount: materials.filter((row) => isLowStock(row)).length,
    zeroStockCount: materials.filter((row) => row.stock <= 0).length,
    estimatedStockValue: materials.reduce((total, row) => total + row.stock * row.unit_price, 0),
  };

  const recentAdjustments = (adjustmentsResult.data ?? []).map((row) => {
    const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
    return {
      id: Number(row.id),
      date: String(row.created_at ?? ""),
      materialId: material?.id ? Number(material.id) : null,
      materialName: material?.name ? String(material.name) : "-",
      unit: material?.unit ? String(material.unit) : null,
      oldStock: Number(row.old_stock ?? 0),
      newStock: Number(row.new_stock ?? 0),
      diff: Number(row.diff ?? 0),
      reason: row.reason ? String(row.reason) : null,
    };
  });

  return {
    ok: true as const,
    summary,
    items: filteredMaterials,
    recentAdjustments,
  };
}

export async function adjustInventory(env: InventoryEnv, payload: InventoryAdjustmentPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const materialId = Number(payload.materialId);
  const newStock = Number(payload.newStock);
  const reason = (payload.reason ?? "").trim() || null;

  if (!Number.isFinite(materialId)) {
    return { ok: false as const, error: "原料編號無效" };
  }

  if (!Number.isFinite(newStock) || newStock < 0) {
    return { ok: false as const, error: "盤點數量必須為 0 以上" };
  }

  const materialResult = await supabase
    .from("raw_materials")
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .eq("id", materialId)
    .maybeSingle();

  if (materialResult.error) {
    return { ok: false as const, error: materialResult.error.message };
  }

  if (!materialResult.data) {
    return { ok: false as const, error: "找不到該原料" };
  }

  const material = mapMaterialRow(materialResult.data);
  const oldStock = Number(material.stock ?? 0);
  const diff = newStock - oldStock;

  const adjustmentInsert = await supabase
    .from("inventory_adjustments")
    .insert({
      material_id: materialId,
      old_stock: oldStock,
      new_stock: newStock,
      diff,
      reason,
    })
    .select("id, old_stock, new_stock, diff, reason, created_at")
    .single();

  if (adjustmentInsert.error) {
    return { ok: false as const, error: adjustmentInsert.error.message };
  }

  const updateResult = await supabase
    .from("raw_materials")
    .update({ stock: newStock })
    .eq("id", materialId)
    .select("id, name, category, brand, vendor, unit, unit_price, stock, safe_stock")
    .single();

  if (updateResult.error) {
    return { ok: false as const, error: updateResult.error.message };
  }

  return {
    ok: true as const,
    item: {
      id: material.id,
      name: material.name,
      category: material.category,
      brand: material.brand,
      vendor: material.vendor,
      unit: material.unit,
      unitPrice: material.unit_price,
      stock: newStock,
      safeStock: material.safe_stock,
      balanceToSafe: newStock - material.safe_stock,
      isLowStock: material.safe_stock > 0 && newStock < material.safe_stock,
    },
    adjustment: {
      id: Number(adjustmentInsert.data.id),
      date: String(adjustmentInsert.data.created_at ?? ""),
      materialId: material.id,
      materialName: material.name,
      unit: material.unit,
      oldStock,
      newStock,
      diff,
      reason,
    },
  };
}
