import { createSupabaseAdmin } from "./supabase";

type DashboardEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

function startOfTodayIso() {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return now.toISOString();
}

function startOfMonthIso() {
  const now = new Date();
  now.setDate(1);
  now.setHours(0, 0, 0, 0);
  return now.toISOString();
}

export async function getDashboardData(env: DashboardEnv) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const today = startOfTodayIso();
  const monthStart = startOfMonthIso();

  const [materialsResult, productsResult, inboundResult, productionResult, salesResult] = await Promise.all([
    supabase.from("raw_materials").select("id, name, stock, safe_stock, unit, vendor, unit_price"),
    supabase.from("products").select("id, name"),
    supabase
      .from("inbound_records")
      .select("id, qty, created_at, raw_materials(name, unit)")
      .order("created_at", { ascending: false })
      .limit(5),
    supabase
      .from("production_logs")
      .select("id, qty, batch_number, created_at, products(name)")
      .order("created_at", { ascending: false })
      .limit(5),
    supabase.from("sales_records").select("id, amount, sale_date, created_at"),
  ]);

  for (const result of [materialsResult, productsResult, inboundResult, productionResult, salesResult]) {
    if (result.error) {
      return { ok: false as const, error: result.error.message };
    }
  }

  const materials = materialsResult.data ?? [];
  const sales = salesResult.data ?? [];

  const summary = {
    lowStockCount: materials.filter((row) => Number(row.safe_stock ?? 0) > 0 && Number(row.stock ?? 0) < Number(row.safe_stock ?? 0)).length,
    todayInboundCount: (inboundResult.data ?? []).filter((row) => String(row.created_at ?? "") >= today).length,
    todayProductionCount: (productionResult.data ?? []).filter((row) => String(row.created_at ?? "") >= today).length,
    todaySalesCount: sales.filter((row) => {
      const dateValue = String(row.sale_date ?? row.created_at ?? "");
      return dateValue >= today;
    }).length,
    monthSalesAmount: sales.reduce((total, row) => {
      const dateValue = String(row.sale_date ?? row.created_at ?? "");
      if (dateValue < monthStart) return total;
      return total + Number(row.amount ?? 0);
    }, 0),
    materialsCount: materials.length,
    productsCount: (productsResult.data ?? []).length,
  };

  const lowStockMaterials = materials
    .filter((row) => Number(row.safe_stock ?? 0) > 0 && Number(row.stock ?? 0) < Number(row.safe_stock ?? 0))
    .sort((a, b) => Number(a.stock ?? 0) - Number(b.stock ?? 0))
    .slice(0, 5)
    .map((row) => ({
      id: Number(row.id),
      name: String(row.name ?? ""),
      stock: Number(row.stock ?? 0),
      safeStock: Number(row.safe_stock ?? 0),
      unit: row.unit ? String(row.unit) : null,
      vendor: row.vendor ? String(row.vendor) : null,
    }));

  const recentInbound = (inboundResult.data ?? []).map((row) => {
    const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
    return {
      id: Number(row.id),
      date: String(row.created_at ?? ""),
      materialName: material?.name ? String(material.name) : "-",
      qty: Number(row.qty ?? 0),
      unit: material?.unit ? String(material.unit) : null,
    };
  });

  const recentProduction = (productionResult.data ?? []).map((row) => {
    const product = Array.isArray(row.products) ? row.products[0] : row.products;
    return {
      id: Number(row.id),
      date: String(row.created_at ?? ""),
      productName: product?.name ? String(product.name) : "-",
      qty: Number(row.qty ?? 0),
      batchNumber: row.batch_number ? String(row.batch_number) : null,
    };
  });

  return {
    ok: true as const,
    summary,
    lowStockMaterials,
    recentInbound,
    recentProduction,
  };
}
