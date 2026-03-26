import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import type { ProductRecord, ProductsResponse } from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

export function ProductsPage() {
  const query = useQuery({
    queryKey: ["products"],
    queryFn: () => apiFetch<ProductsResponse>("/api/products"),
  });

  return (
    <section className="section">
      <div className="section-title">
        <h2>產品主檔</h2>
        <p>這一頁會接續補產品編輯、配方管理與保存期限規則。</p>
      </div>

      <div className="toolbar-card">
        <div>
          <strong>目前進度</strong>
          <p>已接好 `/api/products` 與 Supabase `products` 表的讀取流程。</p>
        </div>
        <span className="pill">Read Only</span>
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
