import { useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import type {
  CreateProductPayload,
  CreateProductResponse,
  ProductRecord,
  ProductsResponse,
} from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

export function ProductsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CreateProductPayload>({
    name: "",
    category: "",
    price: 0,
    cost: 0,
    stock: 0,
    shelfLife: null,
  });

  const query = useQuery({
    queryKey: ["products"],
    queryFn: () => apiFetch<ProductsResponse>("/api/products"),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateProductPayload) =>
      apiFetch<CreateProductResponse>("/api/products", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      setForm({
        name: "",
        category: "",
        price: 0,
        cost: 0,
        stock: 0,
        shelfLife: null,
      });
    },
  });

  const summary = useMemo(() => {
    const items = query.data?.items ?? [];
    return {
      total: items.length,
      withShelfLifeCount: items.filter((item) => item.shelfLife !== null).length,
    };
  }, [query.data]);

  function updateField<K extends keyof CreateProductPayload>(key: K, value: CreateProductPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.reset();
    createMutation.mutate({
      name: form.name.trim(),
      category: form.category?.trim() || null,
      price: Number(form.price ?? 0),
      cost: Number(form.cost ?? 0),
      stock: Number(form.stock ?? 0),
      shelfLife: form.shelfLife === null || form.shelfLife === undefined ? null : Number(form.shelfLife),
    });
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>產品主檔</h2>
        <p>第二個正式可操作模組。現在可新增產品，後續再往配方與 BOM 管理延伸。</p>
      </div>

      <div className="toolbar-card">
        <div>
          <strong>目前進度</strong>
          <p>已接好 `/api/products` 讀寫路徑，新增表單會透過 Worker 寫入 Supabase。</p>
        </div>
        <span className="pill">Create Ready</span>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>新增產品</strong>
            <p>先把產品建檔做穩，下一步就能順手接配方、保存期限規則與生產流程。</p>
          </div>
          <div className="info-row compact">
            <span>產品數：{summary.total}</span>
            <span>有保存期限：{summary.withShelfLifeCount}</span>
          </div>
        </div>

        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>名稱</span>
            <input
              required
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              placeholder="例如：檸檬塔"
            />
          </label>

          <label className="field">
            <span>類別</span>
            <input
              value={form.category ?? ""}
              onChange={(event) => updateField("category", event.target.value)}
              placeholder="例如：常溫蛋糕/塔"
            />
          </label>

          <label className="field">
            <span>售價</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.price ?? 0}
              onChange={(event) => updateField("price", Number(event.target.value))}
            />
          </label>

          <label className="field">
            <span>成本</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.cost ?? 0}
              onChange={(event) => updateField("cost", Number(event.target.value))}
            />
          </label>

          <label className="field">
            <span>起始庫存</span>
            <input
              type="number"
              min="0"
              step="0.001"
              value={form.stock ?? 0}
              onChange={(event) => updateField("stock", Number(event.target.value))}
            />
          </label>

          <label className="field">
            <span>保存期限（天）</span>
            <input
              type="number"
              min="0"
              step="1"
              value={form.shelfLife ?? ""}
              onChange={(event) =>
                updateField("shelfLife", event.target.value === "" ? null : Number(event.target.value))
              }
              placeholder="可留空"
            />
          </label>

          <div className="form-actions">
            <button className="primary-button" type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "新增中..." : "新增產品"}
            </button>
          </div>
        </form>

        {createMutation.isError ? (
          <div className="empty-state error">新增失敗：{String(createMutation.error)}</div>
        ) : null}
        {createMutation.isSuccess ? <div className="empty-state success">新增成功，列表已更新。</div> : null}
      </div>

      {query.isLoading ? <div className="empty-state">正在載入產品資料...</div> : null}
      {query.isError ? <div className="empty-state error">載入失敗：{String(query.error)}</div> : null}

      {query.data ? (
        <>
          <div className="info-row">
            <span>資料來源：{query.data.source}</span>
            <span>筆數：{query.data.items.length}</span>
          </div>
          <div className="table-card">
            <table className="data-table">
              <thead>
                <tr>
                  <th>產品名稱</th>
                  <th>類別</th>
                  <th>售價</th>
                  <th>成本</th>
                  <th>目前庫存</th>
                  <th>保存期限</th>
                </tr>
              </thead>
              <tbody>
                {query.data.items.map((item: ProductRecord) => (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{item.category || "-"}</td>
                    <td>{formatNumber(item.price)}</td>
                    <td>{formatNumber(item.cost)}</td>
                    <td>{formatNumber(item.stock)}</td>
                    <td>{item.shelfLife === null ? "-" : `${item.shelfLife} 天`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}
