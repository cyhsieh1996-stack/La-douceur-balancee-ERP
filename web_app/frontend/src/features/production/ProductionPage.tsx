import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExampleBanner } from "../../components/ExampleBanner";
import { StatusBanner } from "../../components/StatusBanner";
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

type ProductionPageProps = {
  onNavigate: (moduleId: "sales" | "inventory" | "overview") => void;
};

export function ProductionPage({ onNavigate }: ProductionPageProps) {
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

  const canSubmit = productId !== "" && qty !== "" && Number(qty) > 0;
  const shortageCount = previewQuery.data?.shortages.length ?? 0;

  return (
    <section className="section">
      <div className="section-title">
        <h2>產品生產與批號</h2>
        <p>建立產品生產批次，預覽原料扣減情況，並在送出後同步增加產品庫存、扣除原料庫存。</p>
      </div>

      <div className="module-flow">
        <div className="module-step">
          <div className="module-step-label">先看什麼</div>
          <ExampleBanner>
            例如：生產 `檸檬塔 12 個`，批號 `B326-74-01`，有效日期填 `2026-03-28`，備註可寫「晨間批次」。
          </ExampleBanner>
          <div className="workflow-strip">
            <div className="workflow-strip-copy">
              <strong>產品生產流程</strong>
              <div className="workflow-steps">
                <span className="step-chip"><span className="step-chip-index">1</span>選產品</span>
                <span className="step-chip"><span className="step-chip-index">2</span>填數量</span>
                <span className="step-chip"><span className="step-chip-index">3</span>看缺料</span>
                <span className="step-chip"><span className="step-chip-index">4</span>確認登錄</span>
              </div>
            </div>
            <div className="strip-meta">
              <span>最近紀錄 {productionQuery.data?.items.length ?? 0} 筆</span>
            </div>
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">在哪裡操作</div>
          <div className="form-card">
            <div className="form-card-header">
              <div>
                <strong>填寫產品生產資料</strong>
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
                <div className="form-actions-main">
                  <button className="primary-button" type="submit" disabled={!canSubmit || shortageCount > 0 || createMutation.isPending}>
                    {createMutation.isPending ? "生產登錄中..." : "確認生產"}
                  </button>
                </div>
                {!canSubmit || (canSubmit && shortageCount > 0) ? (
                  <div className="form-actions-notes">
                    {!canSubmit ? <span className="form-hint">請先選產品並輸入大於 0 的生產數量。</span> : null}
                    {canSubmit && shortageCount > 0 ? <span className="form-hint danger">目前有缺料，請先補貨再登錄生產。</span> : null}
                  </div>
                ) : null}
              </div>
            </form>

            {createMutation.isError ? <StatusBanner tone="error" title="生產失敗">{String(createMutation.error)}</StatusBanner> : null}
            {createMutation.isSuccess ? (
              <>
                <StatusBanner tone="success" title="生產完成">產品庫存與原料扣減都已更新。</StatusBanner>
                <div className="flow-actions">
                  <button className="secondary-button" type="button" onClick={() => onNavigate("sales")}>
                    下一步：前往 POS 匯入
                  </button>
                  <button className="secondary-button" type="button" onClick={() => onNavigate("inventory")}>
                    查看庫存中心
                  </button>
                  <button className="table-link" type="button" onClick={() => onNavigate("overview")}>
                    回工作台
                  </button>
                </div>
              </>
            ) : null}
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">結果在哪裡看</div>
          <section className="table-card split-card">
            <div className="split-card-header">
              <strong>配方扣料預覽</strong>
              <span className="pill">{previewQuery.data?.items.length ?? 0} 項 / 缺料 {shortageCount}</span>
            </div>
            {!canSubmit ? <div className="empty-state">先選產品並輸入生產數量，系統才會計算這批生產需要扣掉哪些原料。</div> : null}
            {previewQuery.isLoading ? <div className="empty-state">正在計算配方扣料...</div> : null}
            {previewQuery.isError ? <StatusBanner tone="error" title="預覽失敗">{String(previewQuery.error)}</StatusBanner> : null}
            {previewQuery.data && canSubmit ? (
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
                    <tr className="table-row-example">
                      <td className="table-empty-cell" colSpan={5}>這個產品目前尚未設定配方，生產時只會增加產品庫存。</td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            ) : null}
          </section>

          {productionQuery.isLoading ? <div className="empty-state">正在載入最近產品生產紀錄...</div> : null}
          {productionQuery.isError ? <StatusBanner tone="error" title="載入失敗">{String(productionQuery.error)}</StatusBanner> : null}
          {productionQuery.data ? (
            <section className="table-card split-card">
              <div className="split-card-header">
                <strong>最近產品生產紀錄</strong>
                <span className="pill">{productionQuery.data.source} / {productionQuery.data.items.length} 筆</span>
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
                  {productionQuery.data.items.length === 0 ? (
                    <tr className="table-row-example">
                      <td className="table-empty-cell" colSpan={5}>
                        範例：2026-03-26 / 檸檬塔 / 12 / B326-74-01 / 2026-03-28
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </section>
          ) : null}
        </div>
      </div>
    </section>
  );
}
