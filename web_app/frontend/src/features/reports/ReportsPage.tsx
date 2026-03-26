import { useQuery } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type { ReportsResponse } from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

function formatMoney(value: number) {
  return `$${formatNumber(value)}`;
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function ReportsPage() {
  const query = useQuery({
    queryKey: ["reports"],
    queryFn: () => apiFetch<ReportsResponse>("/api/reports"),
  });

  const cards = query.data
    ? [
        { label: "本月銷售", value: formatMoney(query.data.summary.monthSalesAmount), hint: "本月累計銷售金額" },
        { label: "本月訂單", value: query.data.summary.monthSalesOrders, hint: "已匯入的銷售筆數" },
        { label: "本月入庫支出", value: formatMoney(query.data.summary.monthInboundCost), hint: "依入庫單價估算" },
        { label: "本月生產量", value: formatNumber(query.data.summary.monthProductionQty), hint: "所有產品合計產量" },
      ]
    : [];

  return (
    <section className="section">
      <div className="section-title">
        <h2>報表與摘要</h2>
        <p>集中看銷售、支出、熱銷產品與低庫存，不把分析拆散到其他頁。</p>
      </div>

      {query.isLoading ? <StatusBanner tone="loading" title="載入中">正在整理報表資料...</StatusBanner> : null}
      {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

      {query.data ? (
        <div className="module-flow">
          <div className="module-step">
            <div className="module-step-label">先看什麼</div>
          <div className="workflow-strip">
            <div className="workflow-strip-copy">
              <strong>先看這三件事</strong>
              <div className="workflow-steps">
                <span className="step-chip"><span className="step-chip-index">1</span>銷售金額</span>
                <span className="step-chip"><span className="step-chip-index">2</span>入庫支出</span>
                <span className="step-chip"><span className="step-chip-index">3</span>熱銷與低庫存</span>
              </div>
            </div>
            <div className="strip-meta">
              <span>資料來源 {query.data.source}</span>
              <span>熱銷產品 {query.data.topProducts.length} 項</span>
            </div>
          </div>

          <div className="summary-grid">
            {cards.map((card) => (
              <article className="panel" key={card.label}>
                <h3>{card.label}</h3>
                <div className="stat-value">{card.value}</div>
                <p>{card.hint}</p>
              </article>
            ))}
          </div>
          </div>

          <div className="module-step">
            <div className="module-step-label">結果在哪裡看</div>
            <div className="split-grid">
            <section className="table-card split-card">
              <div className="split-card-header">
                <strong>熱銷產品</strong>
                <span className="pill">{query.data.topProducts.length} 項</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>產品</th>
                    <th>訂單數</th>
                    <th>銷售量</th>
                    <th>銷售金額</th>
                  </tr>
                </thead>
                <tbody>
                  {query.data.topProducts.map((item) => (
                    <tr key={item.productName}>
                      <td>{item.productName}</td>
                      <td>{item.orderCount}</td>
                      <td>{formatNumber(item.qty)}</td>
                      <td>{formatMoney(item.amount)}</td>
                    </tr>
                  ))}
                  {query.data.topProducts.length === 0 ? (
                    <tr>
                      <td className="table-empty-cell" colSpan={4}>
                        目前還沒有足夠的銷售資料，等匯入更多 POS 資料後這裡會更有參考價值。
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </section>

            <section className="table-card split-card">
              <div className="split-card-header">
                <strong>低庫存與估值</strong>
                <span className="pill">{query.data.lowStockMaterials.length} 項</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>原料</th>
                    <th>目前庫存</th>
                    <th>安全庫存</th>
                    <th>估算庫存值</th>
                  </tr>
                </thead>
                <tbody>
                  {query.data.lowStockMaterials.map((item) => (
                    <tr key={item.id}>
                      <td>{item.name}</td>
                      <td>{formatNumber(item.stock)} {item.unit ?? ""}</td>
                      <td>{formatNumber(item.safeStock)} {item.unit ?? ""}</td>
                      <td>{formatMoney(item.estimatedValue)}</td>
                    </tr>
                  ))}
                  {query.data.lowStockMaterials.length === 0 ? (
                    <tr>
                      <td className="table-empty-cell" colSpan={4}>
                        目前沒有低庫存原料，這表示安全庫存線大致穩定。
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </section>
            </div>

            <section className="table-card split-card">
            <div className="split-card-header">
              <strong>最近營運異動</strong>
              <span className="pill">{query.data.recentTransactions.length} 筆</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>類型</th>
                  <th>項目</th>
                  <th>數量</th>
                  <th>金額</th>
                </tr>
              </thead>
              <tbody>
                {query.data.recentTransactions.map((item) => (
                  <tr key={item.id}>
                    <td>{formatDate(item.date)}</td>
                    <td>{item.type === "inbound" ? "入庫" : "生產"}</td>
                    <td>{item.label}</td>
                    <td>{formatNumber(item.qty)}</td>
                    <td>{item.amount > 0 ? formatMoney(item.amount) : "-"}</td>
                  </tr>
                ))}
                {query.data.recentTransactions.length === 0 ? (
                  <tr>
                    <td className="table-empty-cell" colSpan={5}>
                      目前還沒有足夠的交易資料，入庫和生產動作累積後會開始出現最近異動摘要。
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </section>
          </div>
        </div>
      ) : null}
    </section>
  );
}
