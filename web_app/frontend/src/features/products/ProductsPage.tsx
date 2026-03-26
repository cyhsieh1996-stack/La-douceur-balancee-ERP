import { useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type {
  CreateProductPayload,
  CreateProductResponse,
  DeleteProductResponse,
  ProductRecord,
  ProductsResponse,
  UpdateProductResponse,
} from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

export function ProductsPage() {
  const queryClient = useQueryClient();
  const [selectedProduct, setSelectedProduct] = useState<ProductRecord | null>(null);
  const [keyword, setKeyword] = useState("");
  const [withShelfLifeOnly, setWithShelfLifeOnly] = useState(false);
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
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: CreateProductPayload) =>
      apiFetch<UpdateProductResponse>(`/api/products/${selectedProduct?.id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (productId: number) =>
      apiFetch<DeleteProductResponse>(`/api/products/${productId}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      resetForm();
    },
  });

  const summary = useMemo(() => {
    const items = query.data?.items ?? [];
    return {
      total: items.length,
      withShelfLifeCount: items.filter((item) => item.shelfLife !== null).length,
    };
  }, [query.data]);

  const filteredItems = useMemo(() => {
    const items = query.data?.items ?? [];
    const normalizedKeyword = keyword.trim().toLowerCase();
    return items.filter((item) => {
      const matchesKeyword =
        normalizedKeyword === "" ||
        [item.name, item.category]
          .map((value) => (value ?? "").toLowerCase())
          .some((value) => value.includes(normalizedKeyword));
      const matchesShelfLife = !withShelfLifeOnly || item.shelfLife !== null;
      return matchesKeyword && matchesShelfLife;
    });
  }, [keyword, withShelfLifeOnly, query.data]);

  function updateField<K extends keyof CreateProductPayload>(key: K, value: CreateProductPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function resetForm() {
    setSelectedProduct(null);
    setForm({
      name: "",
      category: "",
      price: 0,
      cost: 0,
      stock: 0,
      shelfLife: null,
    });
    createMutation.reset();
    updateMutation.reset();
    deleteMutation.reset();
  }

  function startEditing(item: ProductRecord) {
    setSelectedProduct(item);
    setForm({
      name: item.name,
      category: item.category ?? "",
      price: item.price,
      cost: item.cost,
      stock: item.stock,
      shelfLife: item.shelfLife,
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
      price: Number(form.price ?? 0),
      cost: Number(form.cost ?? 0),
      stock: Number(form.stock ?? 0),
      shelfLife: form.shelfLife === null || form.shelfLife === undefined ? null : Number(form.shelfLife),
    };

    if (selectedProduct === null) {
      createMutation.mutate(payload);
      return;
    }

    updateMutation.mutate(payload);
  }

  function handleDeleteProduct() {
    if (!selectedProduct) return;
    if (!window.confirm("確定要刪除這個產品嗎？相關配方也會一併刪除。")) return;
    deleteMutation.reset();
    deleteMutation.mutate(selectedProduct.id);
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>產品</h2>
        <p>維護產品售價、成本、庫存與保存期限。</p>
      </div>

      <div className="module-flow">
        <div className="module-step">
          <div className="module-step-label">先看什麼</div>
          <div className="filter-toolbar">
            <div className="filter-toolbar-main">
              <strong>先找產品，再維護資料</strong>
              <p>先搜尋目標產品，選到後再進行編輯。</p>
              <div className="filter-toolbar-form">
                <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜尋產品名稱、類別" />
                <label className="checkbox-field">
                  <input type="checkbox" checked={withShelfLifeOnly} onChange={(event) => setWithShelfLifeOnly(event.target.checked)} />
                  <span>只看有保存期限</span>
                </label>
                <button className="secondary-button" type="button" onClick={() => {
                  setKeyword("");
                  setWithShelfLifeOnly(false);
                }}>
                  清除篩選
                </button>
              </div>
            </div>
            <div className="filter-toolbar-meta">
              <strong>{selectedProduct ? "目前可編輯產品" : "目前可新增產品"}</strong>
              <p>產品 {summary.total} 筆，有保存期限 {summary.withShelfLifeCount} 筆</p>
            </div>
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">在哪裡操作</div>
        <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>{selectedProduct ? "編輯產品" : "新增產品"}</strong>
            <p>產品資料與配方已分開管理。</p>
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

          <div className="form-actions form-actions-inline-start form-actions-cluster">
            <button
              className="primary-button"
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending || deleteMutation.isPending}
            >
              {selectedProduct
                ? updateMutation.isPending
                  ? "儲存中..."
                  : "儲存修改"
                : createMutation.isPending
                  ? "新增中..."
                  : "新增產品"}
            </button>
            {selectedProduct ? (
              <>
                <button className="secondary-button" type="button" onClick={resetForm}>
                  取消
                </button>
                <button className="danger-button" type="button" onClick={handleDeleteProduct}>
                  {deleteMutation.isPending ? "刪除中..." : "刪除產品"}
                </button>
              </>
            ) : null}
          </div>
        </form>

        {createMutation.isError ? <StatusBanner tone="error" title="新增失敗">{String(createMutation.error)}</StatusBanner> : null}
        {createMutation.isSuccess ? <StatusBanner tone="success" title="新增完成">產品列表已更新。</StatusBanner> : null}
        {updateMutation.isError ? <StatusBanner tone="error" title="儲存失敗">{String(updateMutation.error)}</StatusBanner> : null}
        {updateMutation.isSuccess ? <StatusBanner tone="success" title="儲存完成">產品變更已更新到列表。</StatusBanner> : null}
        {deleteMutation.isError ? <StatusBanner tone="error" title="刪除失敗">{String(deleteMutation.error)}</StatusBanner> : null}
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">結果在哪裡看</div>
          {query.isLoading ? <StatusBanner tone="loading" title="載入中">正在載入產品資料...</StatusBanner> : null}
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
                  <th>產品名稱</th>
                  <th>類別</th>
                  <th>售價</th>
                  <th>成本</th>
                  <th>目前庫存</th>
                  <th>保存期限</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item: ProductRecord) => (
                  <tr
                    key={item.id}
                    data-selected={selectedProduct?.id === item.id ? "true" : "false"}
                    onClick={() => startEditing(item)}
                  >
                    <td>{item.name}</td>
                    <td>{item.category || "-"}</td>
                    <td>{formatNumber(item.price)}</td>
                    <td>{formatNumber(item.cost)}</td>
                    <td>{formatNumber(item.stock)}</td>
                    <td>{item.shelfLife === null ? "-" : `${item.shelfLife} 天`}</td>
                    <td>
                      <button
                        className="table-link"
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          startEditing(item);
                        }}
                      >
                        編輯產品
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan={7}>沒有符合條件的產品資料。</td>
                  </tr>
                ) : null}
              </tbody>
                </table>
              </div>

            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}
