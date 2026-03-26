import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import type { ProductsResponse } from "../products/types";
import type {
  BatchNumberResponse,
  CreateProductionPayload,
  CreateProductionResponse,
  ProductionPreviewResponse,
  ProductionResponse,
} from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

function formatDate(value: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function todayString() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

export function ProductionPage() {
  const queryClient = useQueryClient();
  const [productId, setProductId] = useState("");
  const [qty, setQty] = useState("");
  const [batchNumber, setBatchNumber] = useState("");
  const [expiryDate, setExpiryDate] = useState(todayString());
  const [note, setNote] = useState("");

  const productsQuery = useQuery({
    queryKey: ["products-for-production"],
    queryFn: () => apiFetch<ProductsResponse>("/api/products"),
  });

  const productionQuery = useQuery({
    queryKey: ["production-logs"],
    queryFn: () => apiFetch<ProductionResponse>("/api/production"),
  });

  const batchNumberQuery = useQuery({
    queryKey: ["production-batch-number", productId],
    queryFn: () => apiFetch<BatchNumberResponse>(`/api/production/batch-number?productId=${productId}`),
    enabled: productId !== "",
  });

  const previewQuery = useQuery({
    queryKey: ["production-preview", productId, qty],
    queryFn: () => apiFetch<ProductionPreviewResponse>(`/api/production/preview?productId=${productId}&qty=${qty}`),
    enabled: productId !== "" && qty !== "" && Number(qty) > 0,
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateProductionPayload) =>
      apiFetch<CreateProductionResponse>("/api/production", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["production-logs"] });
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      await queryClient.invalidateQueries({ queryKey: ["products-for-production"] });
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      await queryClient.invalidateQueries({ queryKey: ["inventory-center"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setQty("");
      setNote("");
    },
  });

  useEffect(() => {
    if (batchNumberQuery.data?.batchNumber) {
      setBatchNumber(batchNumberQuery.data.batchNumber);
    }
  }, [batchNumberQuery.data]);

  const selectedProduct = useMemo(
    () => productsQuery.data?.items.find((item) => String(item.id) === productId) ?? null,
    [productsQuery.data, productId],
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.reset();
    createMutation.mutate({
      productId: Number(productId),
      qty: Number(qty),
      batchNumber: batchNumber.trim() || null,
      expiryDate: expiryDate || null,
      note: note.trim() || null,
    });
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>生產與批號</h2>
        <p>建立生產批次，預覽原料扣減情況，並在送出後同步增加產品庫存、扣除原料庫存。</p>
      </div>

      <div className="toolbar-card">
        <div>
          <strong>目前進度</strong>
          <p>已接好 `/api/production`，現在可生成批號、預覽 BOM 扣料並正式登錄生產。</p>
        </div>
        <span className="pill">Production Ready</span>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>新增生產批次</strong>
            <p>先選產品，再輸入生產數量。系統會自動算批號並檢查配方用料是否足夠。</p>
          </div>
          {selectedProduct ? (
            <div className="info-row compact">
              <span>目前產品庫存：{formatNumber(selectedProduct.stock)}</span>
              <span>保存期限：{selectedProduct.shelfLife ?? "-"} 天</span>
            </div>
          ) : null}
        </div>

        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>產品</span>
            <select value={productId} onChange={(event) => setProductId(event.target.value)}>
              <option value="">選擇產品</option>
              {productsQuery.data?.items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>生產數量</span>
            <input
              type="number"
              min="0"
              step="0.001"
              value={qty}
              onChange={(event) => setQty(event.target.value)}
              placeholder="例如：12"
            />
          </label>

          <label className="field">
            <span>批號</span>
            <input value={batchNumber} onChange={(event) => setBatchNumber(event.target.value)} placeholder="自動生成" />
          </label>

          <label className="field">
            <span>有效日期</span>
            <input type="date" value={expiryDate} onChange={(event) => setExpiryDate(event.target.value)} />
          </label>

          <label className="field field-span-2">
            <span>備註</span>
            <input value={note} onChange={(event) => setNote(event.target.value)} placeholder="例如：今日晨間批次、節日備貨" />
          </label>

          <div className="form-actions">
            <button className="primary-button" type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "生產登錄中..." : "確認生產"}
            </button>
          </div>
        </form>

        {createMutation.isError ? <div className="empty-state error">生產失敗：{String(createMutation.error)}</div> : null}
        {createMutation.isSuccess ? <div className="empty-state success">生產成功，庫存與原料已更新。</div> : null}
      </div>

      <section className="table-card split-card">
        <div className="split-card-header">
          <strong>配方扣料預覽</strong>
          <span className="pill">{previewQuery.data?.items.length ?? 0} 項</span>
        </div>
        {previewQuery.isLoading ? <div className="empty-state">正在計算配方扣料...</div> : null}
        {previewQuery.isError ? <div className="empty-state error">預覽失敗：{String(previewQuery.error)}</div> : null}
        {previewQuery.data ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>原料</th>
                <th>每單位用量</th>
                <th>本次需求</th>
                <th>目前庫存</th>
                <th>扣後餘量</th>
              </tr>
            </thead>
            <tbody>
              {previewQuery.data.items.map((item) => (
                <tr key={item.id} data-state={item.isShortage ? "danger" : "normal"}>
                  <td>{item.materialName}</td>
                  <td>
                    {formatNumber(item.qtyPerUnit)} {item.unit ?? ""}
                  </td>
                  <td>
                    {formatNumber(item.requiredQty)} {item.unit ?? ""}
                  </td>
                  <td>
                    {formatNumber(item.currentStock)} {item.unit ?? ""}
                  </td>
                  <td>
                    {formatNumber(item.remainingStock)} {item.unit ?? ""}
                  </td>
                </tr>
              ))}
              {previewQuery.data.items.length === 0 ? (
                <tr>
                  <td colSpan={5}>這個產品目前尚未設定配方，生產時只會增加產品庫存。</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        ) : null}
      </section>

      {productionQuery.isLoading ? <div className="empty-state">正在載入最近生產紀錄...</div> : null}
      {productionQuery.isError ? <div className="empty-state error">載入失敗：{String(productionQuery.error)}</div> : null}
      {productionQuery.data ? (
        <section className="table-card split-card">
          <div className="split-card-header">
            <strong>最近生產紀錄</strong>
            <span className="pill">{productionQuery.data.items.length} 筆</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>產品</th>
                <th>數量</th>
                <th>批號</th>
                <th>有效日期</th>
              </tr>
            </thead>
            <tbody>
              {productionQuery.data.items.map((item) => (
                <tr key={item.id}>
                  <td>{formatDate(item.date)}</td>
                  <td>{item.productName}</td>
                  <td>{formatNumber(item.qty)}</td>
                  <td>{item.batchNumber || "-"}</td>
                  <td>{formatDate(item.expiryDate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}
    </section>
  );
}
