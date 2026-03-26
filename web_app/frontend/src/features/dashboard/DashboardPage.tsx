import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../lib/api";
import type { DashboardResponse } from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function DashboardPage() {
  const query = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardResponse>("/api/dashboard"),
  });

  const cards = query.data
    ? [
        { label: "低庫存警示", value: query.data.summary.lowStockCount, hint: "需要優先補貨" },
        { label: "今日入庫", value: query.data.summary.todayInboundCount, hint: "今日進貨筆數" },
        { label: "今日生產", value: query.data.summary.todayProductionCount, hint: "今日生產筆數" },
        { label: "本月銷售", value: `$${formatNumber(query.data.summary.monthSalesAmount)}`, hint: "累計銷售金額" },
      ]
    : [];

  return (
    <>
      <section className="section">
        <div className="section-title">
          <h2>今日作業</h2>
          <p>沿用桌面版的工作台概念，先把每天最需要看到的摘要與提醒收進來。</p>
        </div>

        {query.isLoading ? <div className="empty-state">正在整理工作台資料...</div> : null}
        {query.isError ? <div className="empty-state error">載入失敗：{String(query.error)}</div> : null}

        {query.data ? (
          <>
            <div className="toolbar-card">
              <div className="toolbar-copy">
                <strong>工作台摘要</strong>
                <p>把低庫存、今日進貨、生產與本月銷售集中在同一頁，方便開工先看一次全局。</p>
              </div>
              <div className="toolbar-actions">
                <span className="pill">資料來源 {query.data.source}</span>
                <span className="pill">低庫存 {query.data.lowStockMaterials.length} 項</span>
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

            <div className="split-grid">
              <section className="table-card split-card">
                <div className="split-card-header">
                  <strong>低庫存原料</strong>
                  <span className="pill">{query.data.lowStockMaterials.length} 筆</span>
                </div>
                {query.data.lowStockMaterials.length === 0 ? (
                  <div className="empty-state">目前沒有低庫存原料。</div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>原料</th>
                        <th>目前庫存</th>
                        <th>安全庫存</th>
                        <th>供應商</th>
                      </tr>
                    </thead>
                    <tbody>
                      {query.data.lowStockMaterials.map((item) => (
                        <tr key={item.id}>
                          <td>{item.name}</td>
                          <td>
                            {formatNumber(item.stock)} {item.unit ?? ""}
                          </td>
                          <td>
                            {formatNumber(item.safeStock)} {item.unit ?? ""}
                          </td>
                          <td>{item.vendor || "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </section>

              <section className="table-card split-card">
                <div className="split-card-header">
                  <strong>最近入庫 / 生產</strong>
                  <span className="pill">Live</span>
                </div>
                <div className="mini-section">
                  <h4>最近入庫</h4>
                  {query.data.recentInbound.length === 0 ? (
                    <div className="empty-state">目前還沒有入庫資料。</div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>日期</th>
                          <th>原料</th>
                          <th>數量</th>
                        </tr>
                      </thead>
                      <tbody>
                        {query.data.recentInbound.map((item) => (
                          <tr key={item.id}>
                            <td>{formatDate(item.date)}</td>
                            <td>{item.materialName}</td>
                            <td>
                              {formatNumber(item.qty)} {item.unit ?? ""}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                <div className="mini-section">
                  <h4>最近生產</h4>
                  {query.data.recentProduction.length === 0 ? (
                    <div className="empty-state">目前還沒有生產資料。</div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>日期</th>
                          <th>產品</th>
                          <th>批號</th>
                        </tr>
                      </thead>
                      <tbody>
                        {query.data.recentProduction.map((item) => (
                          <tr key={item.id}>
                            <td>{formatDate(item.date)}</td>
                            <td>{item.productName}</td>
                            <td>{item.batchNumber || "-"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </section>
            </div>
          </>
        ) : null}
      </section>
    </>
  );
}
