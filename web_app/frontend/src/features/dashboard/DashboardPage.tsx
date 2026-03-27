import { useQuery } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type { DashboardResponse } from "./types";

type DashboardPageProps = {
  onNavigate: (moduleId: "materials" | "inbound" | "production" | "inventory" | "sales" | "reports") => void;
};

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function formatMoney(value: number) {
  return `NT$ ${formatNumber(value)}`;
}

function todayLabel() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  const query = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardResponse>("/api/dashboard"),
  });

  const cards = query.data
    ? [
        { label: "缺貨", value: query.data.summary.zeroStockCount },
        { label: "待補貨", value: query.data.summary.lowStockCount },
        { label: "今日原料入庫", value: query.data.summary.todayInboundCount },
        { label: "今日產品生產", value: query.data.summary.todayProductionCount },
      ]
    : [];

  const recentActivities = query.data
    ? [
        ...query.data.recentInbound.map((item) => ({
          id: `inbound-${item.id}`,
          type: "入庫",
          date: item.date,
          label: item.materialName,
          meta: `${formatNumber(item.qty)} ${item.unit ?? ""}`.trim(),
        })),
        ...query.data.recentProduction.map((item) => ({
          id: `production-${item.id}`,
          type: "生產",
          date: item.date,
          label: item.productName,
          meta: item.batchNumber || "-",
        })),
        ...query.data.recentSales.map((item) => ({
          id: `sales-${item.id}`,
          type: "POS",
          date: item.date,
          label: item.productName,
          meta: item.orderId || `${formatNumber(item.qty)} 件`,
        })),
      ]
        .sort((a, b) => String(b.date).localeCompare(String(a.date)))
        .slice(0, 6)
    : [];

  const closingCards = query.data
    ? [
        { label: "今日原料入庫", value: query.data.summary.todayInboundCount },
        { label: "今日產品生產", value: query.data.summary.todayProductionCount },
        { label: "今日 POS 匯入", value: query.data.summary.todaySalesCount },
        { label: "本日銷售", value: formatMoney(query.data.summary.todaySalesAmount) },
      ]
    : [];

  const focusCopy = query.data
    ? query.data.summary.zeroStockCount > 0
      ? `先補 ${query.data.summary.zeroStockCount} 項缺貨原料，避免今天的生產卡住。`
      : query.data.summary.lowStockCount > 0
        ? `先確認 ${query.data.summary.lowStockCount} 項待補貨原料，再安排今天的生產。`
        : "今天沒有立即缺貨，可直接往原料入庫或產品生產流程前進。"
    : "";

  return (
    <>
      <section className="section">
        <div className="section-title">
          <h2>工作台</h2>
          <p>分成開店前確認與閉店結報兩段，讓一天的流程更清楚。</p>
        </div>

        {query.isLoading ? <StatusBanner tone="loading" title="載入中">正在整理工作台資料...</StatusBanner> : null}
        {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

        {query.data ? (
          <>
            <div className="dashboard-flow">
              <section className="dashboard-section dashboard-section-opening">
                <div className="dashboard-section-header">
                  <div>
                    <span className="dashboard-section-kicker">開店前資訊</span>
                    <h3>開店前確認</h3>
                  </div>
                  <span className="pill">{todayLabel()}</span>
                </div>

                <div className="dashboard-focus">
                  <div>
                    <strong>{focusCopy}</strong>
                  </div>
                </div>

                <div className="dashboard-strip">
                  {cards.map((card) => (
                    <div className="dashboard-metric" key={card.label}>
                      <span>{card.label}</span>
                      <strong>{card.value}</strong>
                    </div>
                  ))}
                </div>

                <div className="action-choice-grid">
                  <button className="action-choice-card" type="button" onClick={() => onNavigate("inventory")}>
                    <span className="action-choice-kicker">先確認</span>
                    <strong>庫存中心</strong>
                    <span className="action-choice-meta">先看缺貨與待補貨</span>
                  </button>
                  <button className="action-choice-card" type="button" onClick={() => onNavigate("inbound")}>
                    <span className="action-choice-kicker">補貨作業</span>
                    <strong>原料入庫</strong>
                    <span className="action-choice-meta">更新原料庫存與單價</span>
                  </button>
                  <button className="action-choice-card" type="button" onClick={() => onNavigate("production")}>
                    <span className="action-choice-kicker">生產作業</span>
                    <strong>產品生產</strong>
                    <span className="action-choice-meta">登錄批次並扣料</span>
                  </button>
                </div>

                <section className="table-card split-card">
                  <div className="split-card-header">
                    <strong>待處理原料</strong>
                    <div className="toolbar-actions">
                      <button className="table-link" type="button" onClick={() => onNavigate("inventory")}>
                        去庫存中心
                      </button>
                      <button className="table-link" type="button" onClick={() => onNavigate("inbound")}>
                        去原料入庫
                      </button>
                    </div>
                  </div>
                  {query.data.lowStockMaterials.length === 0 ? (
                    <div className="empty-state dashboard-empty-state">目前沒有低庫存原料，今天開店前暫時不需要優先補貨。</div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>原料</th>
                          <th>目前</th>
                          <th>安全量</th>
                          <th>狀態</th>
                        </tr>
                      </thead>
                      <tbody>
                        {query.data.lowStockMaterials.map((item) => (
                          <tr key={item.id}>
                            <td>{item.name}</td>
                            <td>{formatNumber(item.stock)} {item.unit ?? ""}</td>
                            <td>{formatNumber(item.safeStock)} {item.unit ?? ""}</td>
                            <td>{item.stock <= 0 ? "缺貨" : "待補貨"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </section>
              </section>

              <section className="dashboard-section dashboard-section-closing">
                <div className="dashboard-section-header">
                  <div>
                    <span className="dashboard-section-kicker">閉店後總結</span>
                    <h3>閉店結報</h3>
                  </div>
                  <div className="toolbar-actions">
                    <button className="table-link" type="button" onClick={() => onNavigate("sales")}>
                      去 POS 匯入
                    </button>
                    <button className="table-link" type="button" onClick={() => onNavigate("reports")}>
                      看報表
                    </button>
                  </div>
                </div>

                <div className="dashboard-closing-strip">
                  {closingCards.map((card) => (
                    <div className="dashboard-closing-metric" key={card.label}>
                      <span>{card.label}</span>
                      <strong>{card.value}</strong>
                    </div>
                  ))}
                </div>

                <section className="table-card split-card">
                  <div className="split-card-header">
                    <strong>今日紀錄</strong>
                  </div>
                  {recentActivities.length === 0 ? (
                    <div className="empty-state dashboard-empty-state">今天還沒有可列入結報的入庫、生產或 POS 匯入紀錄。</div>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>日期</th>
                          <th>類型</th>
                          <th>項目</th>
                          <th>內容</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentActivities.map((item) => (
                          <tr key={item.id}>
                            <td>{formatDate(item.date)}</td>
                            <td>{item.type}</td>
                            <td>{item.label}</td>
                            <td>{item.meta}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </section>
              </section>
            </div>
          </>
        ) : null}
      </section>
    </>
  );
}
