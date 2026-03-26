export type ReportsSummary = {
  monthSalesAmount: number;
  monthSalesOrders: number;
  monthInboundCost: number;
  monthProductionQty: number;
};

export type ReportsTopProduct = {
  productName: string;
  orderCount: number;
  qty: number;
  amount: number;
};

export type ReportsLowStockMaterial = {
  id: number;
  name: string;
  stock: number;
  safeStock: number;
  unit: string | null;
  estimatedValue: number;
};

export type ReportsRecentTransaction = {
  id: string;
  type: "inbound" | "production";
  date: string;
  label: string;
  qty: number;
  amount: number;
};

export type ReportsResponse = {
  ok: true;
  summary: ReportsSummary;
  topProducts: ReportsTopProduct[];
  lowStockMaterials: ReportsLowStockMaterial[];
  recentTransactions: ReportsRecentTransaction[];
  source: "supabase";
};
