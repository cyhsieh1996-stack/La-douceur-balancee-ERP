import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type { MaterialsResponse } from "../materials/types";
import type {
  DeleteRecipeResponse,
  ProductsResponse,
  RecipeRecord,
  RecipesResponse,
  SaveRecipePayload,
  SaveRecipeResponse,
} from "../products/types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

export function RecipesPage() {
  const queryClient = useQueryClient();
  const [productId, setProductId] = useState("");
  const [recipeMaterialId, setRecipeMaterialId] = useState("");
  const [recipeQtyPerUnit, setRecipeQtyPerUnit] = useState("");
  const [recipeNote, setRecipeNote] = useState("");

  const productsQuery = useQuery({
    queryKey: ["products"],
    queryFn: () => apiFetch<ProductsResponse>("/api/products"),
  });

  const materialsQuery = useQuery({
    queryKey: ["materials-for-recipes"],
    queryFn: () => apiFetch<MaterialsResponse>("/api/materials"),
  });

  const recipesQuery = useQuery({
    queryKey: ["product-recipes", productId],
    queryFn: () => apiFetch<RecipesResponse>(`/api/products/${productId}/recipes`),
    enabled: productId !== "",
  });

  const saveRecipeMutation = useMutation({
    mutationFn: (payload: SaveRecipePayload) =>
      apiFetch<SaveRecipeResponse>(`/api/products/${productId}/recipes`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["product-recipes", productId] });
      setRecipeMaterialId("");
      setRecipeQtyPerUnit("");
      setRecipeNote("");
    },
  });

  const deleteRecipeMutation = useMutation({
    mutationFn: (recipeId: number) =>
      apiFetch<DeleteRecipeResponse>(`/api/recipes/${recipeId}`, {
        method: "DELETE",
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["product-recipes", productId] });
    },
  });

  const selectedProduct = useMemo(
    () => productsQuery.data?.items.find((item) => String(item.id) === productId) ?? null,
    [productsQuery.data, productId],
  );

  useEffect(() => {
    if (productId !== "") return;
    const firstProductId = productsQuery.data?.items[0]?.id;
    if (firstProductId) {
      setProductId(String(firstProductId));
    }
  }, [productId, productsQuery.data]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!productId) return;
    saveRecipeMutation.reset();
    saveRecipeMutation.mutate({
      materialId: Number(recipeMaterialId),
      qtyPerUnit: Number(recipeQtyPerUnit),
      note: recipeNote.trim() || null,
    });
  }

  function handleDeleteRecipe(recipe: RecipeRecord) {
    if (!window.confirm(`確定要刪除 ${recipe.materialName} 這條配方嗎？`)) return;
    deleteRecipeMutation.reset();
    deleteRecipeMutation.mutate(recipe.id);
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>配方</h2>
        <p>集中維護產品 BOM，新增後直接在同頁核對完整配方清單。</p>
      </div>

      <div className="module-flow">
        <div className="module-step">
          <div className="module-step-label">先看什麼</div>
          <div className="filter-toolbar">
            <div className="filter-toolbar-main">
              <strong>先選產品，再維護配方</strong>
              <div className="filter-toolbar-form">
                <select
                  className="toolbar-select"
                  value={productId}
                  onChange={(event) => setProductId(event.target.value)}
                >
                  <option value="">選擇產品</option>
                  {productsQuery.data?.items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="filter-toolbar-meta">
              <strong>{selectedProduct ? selectedProduct.name : "尚未選擇產品"}</strong>
              <p>產品 {productsQuery.data?.items.length ?? 0} 筆</p>
            </div>
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">在哪裡操作</div>
          <div className="form-card">
            <div className="form-card-header">
              <div>
                <strong>新增 / 更新配方</strong>
                <p>同一個產品與原料重複儲存時，會直接更新每單位用量。</p>
              </div>
              <div className="info-row compact">
                <span>配方項數：{recipesQuery.data?.items.length ?? 0}</span>
              </div>
            </div>

            <form className="form-grid compact-form" onSubmit={handleSubmit}>
              <label className="field">
                <span>原料</span>
                <select
                  value={recipeMaterialId}
                  onChange={(event) => setRecipeMaterialId(event.target.value)}
                  disabled={materialsQuery.isLoading || !selectedProduct}
                >
                  <option value="">選擇原料</option>
                  {materialsQuery.data?.items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span>每單位用量</span>
                <input
                  type="number"
                  min="0"
                  step="0.001"
                  value={recipeQtyPerUnit}
                  onChange={(event) => setRecipeQtyPerUnit(event.target.value)}
                  placeholder="例如：0.25"
                  disabled={!selectedProduct}
                />
              </label>

              <label className="field field-span-2">
                <span>備註</span>
                <input
                  value={recipeNote}
                  onChange={(event) => setRecipeNote(event.target.value)}
                  placeholder="例如：可替換品牌、特殊備註"
                  disabled={!selectedProduct}
                />
              </label>

              <div className="form-actions form-actions-inline-start form-actions-cluster">
                <button className="primary-button" type="submit" disabled={saveRecipeMutation.isPending || !selectedProduct}>
                  {saveRecipeMutation.isPending ? "儲存中..." : "儲存配方"}
                </button>
              </div>
            </form>

            {!selectedProduct ? <StatusBanner tone="loading" title="請先選擇產品">先選產品，再開始輸入配方。</StatusBanner> : null}
            {recipesQuery.isLoading ? <StatusBanner tone="loading" title="載入中">正在載入配方資料...</StatusBanner> : null}
            {recipesQuery.isError ? <StatusBanner tone="error" title="載入失敗">{String(recipesQuery.error)}</StatusBanner> : null}
            {saveRecipeMutation.isError ? <StatusBanner tone="error" title="配方儲存失敗">{String(saveRecipeMutation.error)}</StatusBanner> : null}
            {saveRecipeMutation.isSuccess ? <StatusBanner tone="success" title="配方已儲存">配方清單已更新。</StatusBanner> : null}
            {deleteRecipeMutation.isError ? <StatusBanner tone="error" title="配方刪除失敗">{String(deleteRecipeMutation.error)}</StatusBanner> : null}
          </div>
        </div>

        <div className="module-step">
          <div className="module-step-label">結果在哪裡看</div>
          {selectedProduct ? (
            <div className="table-card recipe-table-card">
              <div className="split-card-header">
                <strong>{selectedProduct.name} 配方清單</strong>
                <span className="pill">{recipesQuery.data?.items.length ?? 0} 項</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>原料</th>
                    <th>每單位用量</th>
                    <th>目前庫存</th>
                    <th>備註</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {recipesQuery.data?.items.map((item) => (
                    <tr key={item.id}>
                      <td>{item.materialName}</td>
                      <td>
                        {formatNumber(item.qtyPerUnit)} {item.unit ?? ""}
                      </td>
                      <td>
                        {formatNumber(item.currentStock)} {item.unit ?? ""}
                      </td>
                      <td>{item.note || "-"}</td>
                      <td>
                        <button className="table-link danger-link" type="button" onClick={() => handleDeleteRecipe(item)}>
                          刪除
                        </button>
                      </td>
                    </tr>
                  ))}
                  {recipesQuery.data && recipesQuery.data.items.length === 0 ? (
                    <tr>
                      <td colSpan={5}>目前還沒有配方，先新增第一筆原料用量。</td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">請先選擇產品，這裡才會顯示配方清單。</div>
          )}
        </div>
      </div>
    </section>
  );
}
