export type SalesRecord = {
  id: number;
  date: string;
  orderId: string | null;
  productName: string;
  qty: number;
  price: number;
  amount: number;
};

export type SalesResponse = {
  ok: true;
  items: SalesRecord[];
  source: "supabase";
};

export type SalesImportPayload = {
  rows: Array<{
    productName: string;
    qty: number;
    price: number;
    amount: number;
    saleDate?: string | null;
    orderId?: string | null;
  }>;
};

export type SalesImportResponse = {
  ok: true;
  importedCount: number;
  source: "supabase";
};
