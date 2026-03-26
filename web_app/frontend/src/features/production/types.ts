export type ProductionRecord = {
  id: number;
  productId: number | null;
  productName: string;
  qty: number;
  batchNumber: string | null;
  expiryDate: string | null;
  note: string | null;
  date: string;
};

export type ProductionResponse = {
  ok: true;
  items: ProductionRecord[];
  source: "supabase";
};

export type BatchNumberResponse = {
  ok: true;
  batchNumber: string;
  source: "supabase";
};

export type ProductionPreviewItem = {
  id: number;
  materialId: number;
  materialName: string;
  unit: string | null;
  currentStock: number;
  qtyPerUnit: number;
  requiredQty: number;
  remainingStock: number;
  note: string | null;
  isShortage: boolean;
};

export type ProductionPreviewResponse = {
  ok: true;
  items: ProductionPreviewItem[];
  shortages: ProductionPreviewItem[];
  source: "supabase";
};

export type CreateProductionPayload = {
  productId: number;
  qty: number;
  batchNumber?: string | null;
  expiryDate?: string | null;
  note?: string | null;
};

export type CreateProductionResponse = {
  ok: true;
  item: ProductionRecord;
  recipePreview: ProductionPreviewItem[];
  source: "supabase";
};
