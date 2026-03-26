import { useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import type {
  CreateMaterialPayload,
  CreateMaterialResponse,
  MaterialsResponse,
  RawMaterial,
} from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

function getStockState(item: RawMaterial) {
  if (item.safeStock > 0 && item.stock < item.safeStock) return "warning";
  if (item.stock <= 0) return "danger";
  return "normal";
}

export function MaterialsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CreateMaterialPayload>({
    name: "",
    category: "",
    brand: "",
    vendor: "",
    unit: "kg",
    unitPrice: 0,
    stock: 0,
    safeStock: 0,
  });

  const query = useQuery({
    queryKey: ["materials"],
    queryFn: () => apiFetch<MaterialsResponse>("/api/materials"),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateMaterialPayload) =>
      apiFetch<CreateMaterialResponse>("/api/materials", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      setForm({
        name: "",
        category: "",
        brand: "",
        vendor: "",
        unit: "kg",
        unitPrice: 0,
        stock: 0,
        safeStock: 0,
      });
    },
  });

  const summary = useMemo(() => {
    const items = query.data?.items ?? [];
    return {
      total: items.length,
      lowStockCount: items.filter((item) => item.safeStock > 0 && item.stock < item.safeStock).length,
    };
  }, [query.data]);

  function updateField<K extends keyof CreateMaterialPayload>(key: K, value: CreateMaterialPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.reset();
    createMutation.mutate({
      name: form.name.trim(),
      category: form.category?.trim() || null,
      brand: form.brand?.trim() || null,
      vendor: form.vendor?.trim() || null,
      unit: form.unit?.trim() || null,
      unitPrice: Number(form.unitPrice ?? 0),
      stock: Number(form.stock ?? 0),
      safeStock: Number(form.safeStock ?? 0),
    });
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>原料主檔</h2>
        <p>第一個正式可操作模組。現在已可從 Web 端新增原料並即時刷新列表。</p>
      </div>

      <div className="toolbar-card">
        <div>
          <strong>目前進度</strong>
          <p>已接好 `/api/materials` 讀寫路徑，新增表單會透過 Worker 寫入 Supabase。</p>
        </div>
        <span className="pill">Create Ready</span>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>新增原料</strong>
            <p>先把第一個寫入流程做穩，後續再補編輯、搜尋與批次匯入。</p>
          </div>
          <div className="info-row compact">
            <span>原料數：{summary.total}</span>
            <span>低庫存：{summary.lowStockCount}</span>
          </div>
        </div>

        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>名稱</span>
            <input
              required
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              placeholder="例如：高筋麵粉"
            />
          </label>

          <label className="field">
            <span>類別</span>
            <input
              value={form.category ?? ""}
              onChange={(event) => updateField("category", event.target.value)}
              placeholder="例如：粉類"
            />
          </label>

          <label className="field">
            <span>廠牌</span>
            <input
              value={form.brand ?? ""}
              onChange={(event) => updateField("brand", event.target.value)}
              placeholder="例如：日清"
            />
          </label>

          <label className="field">
            <span>廠商</span>
            <input
              value={form.vendor ?? ""}
              onChange={(event) => updateField("vendor", event.target.value)}
              placeholder="例如：大統食品"
            />
          </label>

          <label className="field">
            <span>單位</span>
            <input
              value={form.unit ?? ""}
              onChange={(event) => updateField("unit", event.target.value)}
              placeholder="kg"
            />
          </label>

          <label className="field">
            <span>單價</span>
            <input
              type="number"
              min="0"
              step="0.001"
              value={form.unitPrice ?? 0}
              onChange={(event) => updateField("unitPrice", Number(event.target.value))}
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
            <span>安全庫存</span>
            <input
              type="number"
              min="0"
              step="0.001"
              value={form.safeStock ?? 0}
              onChange={(event) => updateField("safeStock", Number(event.target.value))}
            />
          </label>

          <div className="form-actions">
            <button className="primary-button" type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "新增中..." : "新增原料"}
            </button>
          </div>
        </form>

        {createMutation.isError ? (
          <div className="empty-state error">新增失敗：{String(createMutation.error)}</div>
        ) : null}
        {createMutation.isSuccess ? <div className="empty-state success">新增成功，列表已更新。</div> : null}
      </div>

      {query.isLoading ? <div className="empty-state">正在載入原料資料...</div> : null}
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
                  <th>原料名稱</th>
                  <th>類別</th>
                  <th>廠牌</th>
                  <th>廠商</th>
                  <th>單位</th>
                  <th>單價</th>
                  <th>庫存</th>
                  <th>安全庫存</th>
                </tr>
              </thead>
              <tbody>
                {query.data.items.map((item) => (
                  <tr key={item.id} data-state={getStockState(item)}>
                    <td>{item.name}</td>
                    <td>{item.category || "-"}</td>
                    <td>{item.brand || "-"}</td>
                    <td>{item.vendor || "-"}</td>
                    <td>{item.unit || "-"}</td>
                    <td>{formatNumber(item.unitPrice)}</td>
                    <td>{formatNumber(item.stock)}</td>
                    <td>{formatNumber(item.safeStock)}</td>
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
