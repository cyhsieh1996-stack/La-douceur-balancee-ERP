import { createSupabaseAdmin } from "./supabase";

type DashboardEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

const DASHBOARD_TIME_ZONE = "Asia/Taipei";

function formatDateKey(value: string | Date | null | undefined) {
  if (!value) return "";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-CA", {
    timeZone: DASHBOARD_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

function currentDateKey() {
  return formatDateKey(new Date());
}

function currentMonthKey() {
  const now = new Date();
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: DASHBOARD_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
  }).format(now);
}

export async function getDashboardData(env: DashboardEnv) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const todayKey = currentDateKey();
  const monthKey = currentMonthKey();

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
    supabase.from("sales_records").select("id, product_name, qty, amount, sale_date, order_id, created_at"),
  ]);

  for (const result of [materialsResult, productsResult, inboundResult, productionResult, salesResult]) {
    if (result.error) {
      return { ok: false as const, error: result.error.message };
    }
  }

  const materials = materialsResult.data ?? [];
  const sales = salesResult.data ?? [];

  const summary = {
    zeroStockCount: materials.filter((row) => Number(row.stock ?? 0) <= 0).length,
    lowStockCount: materials.filter((row) => Number(row.safe_stock ?? 0) > 0 && Number(row.stock ?? 0) < Number(row.safe_stock ?? 0)).length,
    todayInboundCount: (inboundResult.data ?? []).filter((row) => formatDateKey(String(row.created_at ?? "")) === todayKey).length,
    todayProductionCount: (productionResult.data ?? []).filter((row) => formatDateKey(String(row.created_at ?? "")) === todayKey).length,
    todaySalesCount: sales.filter((row) => {
      const dateValue = formatDateKey(String(row.sale_date ?? row.created_at ?? ""));
      return dateValue === todayKey;
    }).length,
    todaySalesAmount: sales.reduce((total, row) => {
      const dateValue = formatDateKey(String(row.sale_date ?? row.created_at ?? ""));
      if (dateValue !== todayKey) return total;
      return total + Number(row.amount ?? 0);
    }, 0),
    monthSalesAmount: sales.reduce((total, row) => {
      const date = row.sale_date ?? row.created_at;
      const dateValue = date ? formatDateKey(String(date)).slice(0, 7) : "";
      if (dateValue !== monthKey) return total;
      return total + Number(row.amount ?? 0);
    }, 0),
    materialsCount: materials.length,
    productsCount: (productsResult.data ?? []).length,
  };

  const lowStockMaterials = materials
    .filter((row) => Number(row.safe_stock ?? 0) > 0 && Number(row.stock ?? 0) < Number(row.safe_stock ?? 0))
    .sort((a, b) => {
      const aStock = Number(a.stock ?? 0);
      const bStock = Number(b.stock ?? 0);
      if (aStock <= 0 && bStock > 0) return -1;
      if (bStock <= 0 && aStock > 0) return 1;
      return aStock - bStock;
    })
    .slice(0, 5)
    .map((row) => ({
      id: Number(row.id),
      name: String(row.name ?? ""),
      stock: Number(row.stock ?? 0),
      safeStock: Number(row.safe_stock ?? 0),
      unit: row.unit ? String(row.unit) : null,
      vendor: row.vendor ? String(row.vendor) : null,
    }));

  const recentInbound = (inboundResult.data ?? [])
    .filter((row) => formatDateKey(String(row.created_at ?? "")) === todayKey)
    .map((row) => {
      const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
      return {
        id: Number(row.id),
        date: String(row.created_at ?? ""),
        materialName: material?.name ? String(material.name) : "-",
        qty: Number(row.qty ?? 0),
        unit: material?.unit ? String(material.unit) : null,
      };
    })
    .slice(0, 5);

  const recentProduction = (productionResult.data ?? [])
    .filter((row) => formatDateKey(String(row.created_at ?? "")) === todayKey)
    .map((row) => {
      const product = Array.isArray(row.products) ? row.products[0] : row.products;
      return {
        id: Number(row.id),
        date: String(row.created_at ?? ""),
        productName: product?.name ? String(product.name) : "-",
        qty: Number(row.qty ?? 0),
        batchNumber: row.batch_number ? String(row.batch_number) : null,
      };
    })
    .slice(0, 5);

  const recentSales = sales
    .filter((row) => {
      const date = row.sale_date ?? row.created_at;
      return formatDateKey(String(date ?? "")) === todayKey;
    })
    .map((row) => ({
      id: Number(row.id),
      date: String(row.sale_date ?? row.created_at ?? ""),
      productName: row.product_name ? String(row.product_name) : "-",
      qty: Number(row.qty ?? 0),
      orderId: row.order_id ? String(row.order_id) : null,
    }))
    .slice(0, 5);

  return {
    ok: true as const,
    summary,
    lowStockMaterials,
    recentInbound,
    recentProduction,
    recentSales,
  };
}
