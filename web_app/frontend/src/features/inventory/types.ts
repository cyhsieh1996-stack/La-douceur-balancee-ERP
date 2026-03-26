export type InventorySummary = {
  materialCount: number;
  lowStockCount: number;
  zeroStockCount: number;
  estimatedStockValue: number;
};

export type InventoryItem = {
  id: number;
  name: string;
  category: string | null;
  brand: string | null;
  vendor: string | null;
  unit: string | null;
  unitPrice: number;
  stock: number;
  safeStock: number;
  balanceToSafe: number;
  isLowStock: boolean;
};

export type InventoryAdjustmentRecord = {
  id: number;
  date: string;
  materialId: number | null;
  materialName: string;
  unit: string | null;
  oldStock: number;
  newStock: number;
  diff: number;
  reason: string | null;
};

export type InventoryCenterResponse = {
  ok: true;
  summary: InventorySummary;
  items: InventoryItem[];
  recentAdjustments: InventoryAdjustmentRecord[];
  source: "supabase";
};

export type InventoryAdjustmentPayload = {
  materialId: number;
  newStock: number;
  reason?: string | null;
};

export type InventoryAdjustmentResponse = {
  ok: true;
  item: InventoryItem;
  adjustment: InventoryAdjustmentRecord;
  source: "supabase";
};
