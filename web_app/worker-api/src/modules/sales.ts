import { createSupabaseAdmin } from "./supabase";

type SalesEnv = {
  SUPABASE_URL?: string;
  SUPABASE_SERVICE_ROLE_KEY?: string;
};

type SalesPayload = {
  rows?: Array<{
    productName?: string;
    qty?: number;
    price?: number;
    amount?: number;
    saleDate?: string | null;
    orderId?: string | null;
  }>;
};

function mapSalesRow(row: Record<string, unknown>) {
  return {
    id: Number(row.id),
    date: String(row.sale_date ?? row.created_at ?? ""),
    orderId: row.order_id ? String(row.order_id) : null,
    productName: String(row.product_name ?? ""),
    qty: Number(row.qty ?? 0),
    price: Number(row.price ?? 0),
    amount: Number(row.amount ?? 0),
  };
}

export async function listSalesRecords(env: SalesEnv, limit = 100) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const { data, error } = await supabase
    .from("sales_records")
    .select("id, product_name, qty, price, amount, sale_date, order_id, created_at")
    .order("sale_date", { ascending: false })
    .limit(limit);

  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    items: (data ?? []).map((row) => mapSalesRow(row)),
  };
}

export async function importSalesRecords(env: SalesEnv, payload: SalesPayload) {
  const supabase = createSupabaseAdmin(env);
  if (!supabase) {
    return { ok: false as const, error: "Supabase admin client is not configured." };
  }

  const rows = payload.rows ?? [];
  if (rows.length === 0) {
    return { ok: false as const, error: "沒有可匯入的銷售資料" };
  }

  const normalizedRows = rows.map((row, index) => {
    const productName = (row.productName ?? "").trim();
    const qty = Number(row.qty);
    const price = Number(row.price);
    const amount = Number(row.amount);
    const saleDate = (row.saleDate ?? "").trim() || new Date().toISOString();
    const orderId = (row.orderId ?? "").trim() || `WEB-POS-${Date.now()}-${index + 1}`;

    if (!productName) {
      throw new Error(`第 ${index + 1} 筆：產品名稱不可空白`);
    }
    if (!Number.isFinite(qty) || qty <= 0) {
      throw new Error(`第 ${index + 1} 筆：數量必須大於 0`);
    }
    if (!Number.isFinite(amount) || amount < 0) {
      throw new Error(`第 ${index + 1} 筆：金額不得小於 0`);
    }

    return {
      product_name: productName,
      qty,
      price: Number.isFinite(price) && price >= 0 ? price : qty === 0 ? 0 : amount / qty,
      amount,
      sale_date: saleDate,
      order_id: orderId,
    };
  });

  const { error } = await supabase.from("sales_records").insert(normalizedRows);
  if (error) {
    return { ok: false as const, error: error.message };
  }

  return {
    ok: true as const,
    importedCount: normalizedRows.length,
  };
}
