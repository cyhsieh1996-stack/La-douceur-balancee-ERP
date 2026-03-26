import { createSupabaseAdmin } from "./supabase";

type ReportsEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

function startOfMonthIso() {
  const now = new Date();
  now.setDate(1);
  now.setHours(0, 0, 0, 0);
  return now.toISOString();
}

function mapTopProducts(rows: Array<Record<string, unknown>>) {
  const grouped = new Map<
    string,
    {
      productName: string;
      orderCount: number;
      qty: number;
      amount: number;
    }
  >();

  for (const row of rows) {
    const productName = String(row.product_name ?? "").trim() || "未命名產品";
    const current = grouped.get(productName) ?? {
      productName,
      orderCount: 0,
      qty: 0,
      amount: 0,
    };

    current.orderCount += 1;
    current.qty += Number(row.qty ?? 0);
    current.amount += Number(row.amount ?? 0);
    grouped.set(productName, current);
  }

  return Array.from(grouped.values())
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5);
}

export async function getReportsData(env: ReportsEnv) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const monthStart = startOfMonthIso();

  const [salesResult, inboundResult, productionResult, materialsResult] = await Promise.all([
    supabase
      .from("sales_records")
      .select("id, product_name, qty, amount, sale_date, created_at, order_id")
      .order("sale_date", { ascending: false })
      .limit(200),
    supabase
      .from("inbound_records")
      .select("id, qty, unit_price, created_at, raw_materials(name, unit)")
      .order("created_at", { ascending: false })
      .limit(100),
    supabase
      .from("production_logs")
      .select("id, qty, batch_number, created_at, products(name)")
      .order("created_at", { ascending: false })
      .limit(100),
    supabase
      .from("raw_materials")
      .select("id, name, stock, safe_stock, unit, unit_price")
      .order("stock", { ascending: true })
      .limit(100),
  ]);

  for (const result of [salesResult, inboundResult, productionResult, materialsResult]) {
    if (result.error) {
      return { ok: false as const, error: result.error.message };
    }
  }

  const salesRows = (salesResult.data ?? []).filter((row) => {
    const dateValue = String(row.sale_date ?? row.created_at ?? "");
    return dateValue >= monthStart;
  });
  const inboundRows = (inboundResult.data ?? []).filter((row) => String(row.created_at ?? "") >= monthStart);
  const productionRows = (productionResult.data ?? []).filter((row) => String(row.created_at ?? "") >= monthStart);
  const materialRows = materialsResult.data ?? [];

  const summary = {
    monthSalesAmount: salesRows.reduce((total, row) => total + Number(row.amount ?? 0), 0),
    monthSalesOrders: salesRows.length,
    monthInboundCost: inboundRows.reduce(
      (total, row) => total + Number(row.qty ?? 0) * Number(row.unit_price ?? 0),
      0,
    ),
    monthProductionQty: productionRows.reduce((total, row) => total + Number(row.qty ?? 0), 0),
  };

  const topProducts = mapTopProducts(salesRows);

  const lowStockMaterials = materialRows
    .filter((row) => Number(row.safe_stock ?? 0) > 0 && Number(row.stock ?? 0) < Number(row.safe_stock ?? 0))
    .slice(0, 5)
    .map((row) => ({
      id: Number(row.id),
      name: String(row.name ?? ""),
      stock: Number(row.stock ?? 0),
      safeStock: Number(row.safe_stock ?? 0),
      unit: row.unit ? String(row.unit) : null,
      estimatedValue: Number(row.stock ?? 0) * Number(row.unit_price ?? 0),
    }));

  const recentTransactions = [
    ...inboundRows.slice(0, 5).map((row) => {
      const material = Array.isArray(row.raw_materials) ? row.raw_materials[0] : row.raw_materials;
      return {
        id: `inbound-${row.id}`,
        type: "inbound" as const,
        date: String(row.created_at ?? ""),
        label: material?.name ? String(material.name) : "-",
        qty: Number(row.qty ?? 0),
        amount: Number(row.qty ?? 0) * Number(row.unit_price ?? 0),
      };
    }),
    ...productionRows.slice(0, 5).map((row) => {
      const product = Array.isArray(row.products) ? row.products[0] : row.products;
      return {
        id: `production-${row.id}`,
        type: "production" as const,
        date: String(row.created_at ?? ""),
        label: product?.name ? String(product.name) : "-",
        qty: Number(row.qty ?? 0),
        amount: 0,
      };
    }),
  ]
    .sort((a, b) => String(b.date).localeCompare(String(a.date)))
    .slice(0, 8);

  return {
    ok: true as const,
    summary,
    topProducts,
    lowStockMaterials,
    recentTransactions,
  };
}
