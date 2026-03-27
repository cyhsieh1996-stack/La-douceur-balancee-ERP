export type DashboardSummary = {
  zeroStockCount: number;
  lowStockCount: number;
  todayInboundCount: number;
  todayProductionCount: number;
  todaySalesCount: number;
  monthSalesAmount: number;
  materialsCount: number;
  productsCount: number;
};

export type DashboardLowStockItem = {
  id: number;
  name: string;
  stock: number;
  safeStock: number;
  unit: string | null;
  vendor: string | null;
};

export type DashboardInboundItem = {
  id: number;
  date: string;
  materialName: string;
  qty: number;
  unit: string | null;
};

export type DashboardProductionItem = {
  id: number;
  date: string;
  productName: string;
  qty: number;
  batchNumber: string | null;
};

export type DashboardSalesItem = {
  id: number;
  date: string;
  productName: string;
  qty: number;
  orderId: string | null;
};

export type DashboardResponse = {
  ok: true;
  summary: DashboardSummary;
  lowStockMaterials: DashboardLowStockItem[];
  recentInbound: DashboardInboundItem[];
  recentProduction: DashboardProductionItem[];
  recentSales: DashboardSalesItem[];
  source: "supabase";
};
