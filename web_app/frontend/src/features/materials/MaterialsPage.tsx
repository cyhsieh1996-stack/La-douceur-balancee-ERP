import { useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type {
  CreateMaterialPayload,
  CreateMaterialResponse,
  DeleteMaterialResponse,
  MaterialsResponse,
  RawMaterial,
  UpdateMaterialResponse,
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
  const [editingId, setEditingId] = useState<number | null>(null);
  const [keyword, setKeyword] = useState("");
  const [lowStockOnly, setLowStockOnly] = useState(false);
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
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: CreateMaterialPayload) =>
      apiFetch<UpdateMaterialResponse>(`/api/materials/${editingId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      apiFetch<DeleteMaterialResponse>(`/api/materials/${id}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      resetForm();
    },
  });

  const summary = useMemo(() => {
    const items = query.data?.items ?? [];
    return {
      total: items.length,
      lowStockCount: items.filter((item) => item.safeStock > 0 && item.stock < item.safeStock).length,
    };
  }, [query.data]);

  const filteredItems = useMemo(() => {
    const items = query.data?.items ?? [];
    const normalizedKeyword = keyword.trim().toLowerCase();
    return items.filter((item) => {
      const matchesKeyword =
        normalizedKeyword === "" ||
        [item.name, item.category, item.brand, item.vendor]
          .map((value) => (value ?? "").toLowerCase())
          .some((value) => value.includes(normalizedKeyword));

      const matchesLowStock = !lowStockOnly || (item.safeStock > 0 && item.stock < item.safeStock);
      return matchesKeyword && matchesLowStock;
    });
  }, [keyword, lowStockOnly, query.data]);

  function updateField<K extends keyof CreateMaterialPayload>(key: K, value: CreateMaterialPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function resetForm() {
    setEditingId(null);
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
    createMutation.reset();
    updateMutation.reset();
    deleteMutation.reset();
  }

  function startEditing(item: RawMaterial) {
    setEditingId(item.id);
    setForm({
      name: item.name,
      category: item.category ?? "",
      brand: item.brand ?? "",
      vendor: item.vendor ?? "",
      unit: item.unit ?? "",
      unitPrice: item.unitPrice,
      stock: item.stock,
      safeStock: item.safeStock,
    });
    createMutation.reset();
    updateMutation.reset();
    deleteMutation.reset();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.reset();
    updateMutation.reset();
    const payload = {
      name: form.name.trim(),
      category: form.category?.trim() || null,
      brand: form.brand?.trim() || null,
      vendor: form.vendor?.trim() || null,
      unit: form.unit?.trim() || null,
      unitPrice: Number(form.unitPrice ?? 0),
      stock: Number(form.stock ?? 0),
      safeStock: Number(form.safeStock ?? 0),
    };

    if (editingId === null) {
      createMutation.mutate(payload);
      return;
    }

    updateMutation.mutate(payload);
  }

  function handleDelete() {
    if (editingId === null) {
      return;
    }

    const confirmed = window.confirm("確定要刪除這筆原料嗎？此操作無法復原。");
    if (!confirmed) {
      return;
    }

    deleteMutation.reset();
    deleteMutation.mutate(editingId);
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>原料主檔</h2>
        <p>維護原料名稱、供應商、單價與安全庫存。</p>
      </div>

      <div className="toolbar-card">
        <div className="toolbar-copy">
          <strong>篩選與狀態</strong>
          <p>先找出要維護的原料，再決定新增、修改或刪除。</p>
        </div>
        <div className="toolbar-actions">
          <div className="filter-form">
            <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜尋名稱、類別、廠牌、廠商" />
            <label className="checkbox-field">
              <input type="checkbox" checked={lowStockOnly} onChange={(event) => setLowStockOnly(event.target.checked)} />
              <span>只看低庫存</span>
            </label>
            <button className="secondary-button" type="button" onClick={() => {
              setKeyword("");
              setLowStockOnly(false);
            }}>
              清除篩選
            </button>
          </div>
          <span className="pill">{editingId === null ? "Create Ready" : "Edit Mode"}</span>
        </div>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>{editingId === null ? "新增原料" : "編輯原料"}</strong>
            <p>
              {editingId === null
                ? "把原料基本資料一次填好，後續入庫與庫存都會直接沿用。"
                : "點選表格列即可帶入編輯，也可以直接刪除這筆原料。"}
            </p>
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
            <button
              className="primary-button"
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending || deleteMutation.isPending}
            >
              {editingId === null
                ? createMutation.isPending
                  ? "新增中..."
                  : "新增原料"
                : updateMutation.isPending
                  ? "儲存中..."
                  : "儲存變更"}
            </button>
            {editingId !== null ? (
              <>
                <button className="secondary-button" type="button" onClick={resetForm} disabled={deleteMutation.isPending}>
                  取消
                </button>
                <button className="danger-button" type="button" onClick={handleDelete} disabled={deleteMutation.isPending}>
                  {deleteMutation.isPending ? "刪除中..." : "刪除"}
                </button>
              </>
            ) : null}
          </div>
        </form>

        {createMutation.isError ? <StatusBanner tone="error" title="新增失敗">{String(createMutation.error)}</StatusBanner> : null}
        {createMutation.isSuccess ? <StatusBanner tone="success" title="新增完成">原料列表已更新。</StatusBanner> : null}
        {updateMutation.isError ? <StatusBanner tone="error" title="儲存失敗">{String(updateMutation.error)}</StatusBanner> : null}
        {updateMutation.isSuccess ? <StatusBanner tone="success" title="儲存完成">原料變更已更新到列表。</StatusBanner> : null}
        {deleteMutation.isError ? <StatusBanner tone="error" title="刪除失敗">{String(deleteMutation.error)}</StatusBanner> : null}
        {deleteMutation.isSuccess ? <StatusBanner tone="success" title="刪除完成">原料已移除，列表已更新。</StatusBanner> : null}
      </div>

      {query.isLoading ? <StatusBanner tone="loading" title="載入中">正在載入原料資料...</StatusBanner> : null}
      {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

      {query.data ? (
        <>
          <div className="info-row">
            <span>資料來源：{query.data.source}</span>
            <span>顯示筆數：{filteredItems.length}</span>
            <span>總筆數：{query.data.items.length}</span>
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
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr
                    key={item.id}
                    data-state={getStockState(item)}
                    data-selected={editingId === item.id ? "true" : "false"}
                    onClick={() => startEditing(item)}
                  >
                    <td>{item.name}</td>
                    <td>{item.category || "-"}</td>
                    <td>{item.brand || "-"}</td>
                    <td>{item.vendor || "-"}</td>
                    <td>{item.unit || "-"}</td>
                    <td>{formatNumber(item.unitPrice)}</td>
                    <td>{formatNumber(item.stock)}</td>
                    <td>{formatNumber(item.safeStock)}</td>
                    <td>
                      <button
                        className="table-link"
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          startEditing(item);
                        }}
                      >
                        編輯
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan={9}>沒有符合條件的原料資料。</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}
