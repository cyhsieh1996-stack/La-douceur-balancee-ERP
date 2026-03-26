export type InboundRecord = {
  id: number;
  date: string;
  materialId: number | null;
  materialName: string;
  unit: string | null;
  qty: number;
  unitPrice: number;
  batchNumber: string | null;
  expiryDate: string | null;
  note: string | null;
};

export type InboundResponse = {
  ok: true;
  items: InboundRecord[];
  source: "supabase";
};

export type CreateInboundPayload = {
  materialId: number;
  qty: number;
  unitPrice?: number;
  batchNumber?: string | null;
  expiryDate?: string | null;
  note?: string | null;
};

export type CreateInboundResponse = {
  ok: true;
  item: InboundRecord;
  material: {
    id: number;
    name: string;
    unit: string | null;
    stock: number;
    unitPrice: number;
  };
  source: "supabase";
};
