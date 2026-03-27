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
        { label: "今日 POS 匯入", value: query.data.summary.todaySalesCount },
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

  const focusCopy = query.data
    ? query.data.summary.zeroStockCount > 0
      ? `先補 ${query.data.summary.zeroStockCount} 項缺貨原料，避免今天的生產卡住。`
      : query.data.summary.lowStockCount > 0
        ? `先確認 ${query.data.summary.lowStockCount} 項待補貨原料，再安排今天的生產。`
        : query.data.summary.todaySalesCount > 0
          ? `今天已同步 ${query.data.summary.todaySalesCount} 筆 POS 匯入，可直接確認庫存與報表是否一致。`
        : "今天沒有立即缺貨，可直接往原料入庫、產品生產或 POS 匯入流程前進。"
    : "";

  return (
    <>
      <section className="section">
        <div className="section-title">
          <h2>開工重點</h2>
          <p>這裡只放一開工就必須知道，而且要優先處理的事情。</p>
        </div>

        {query.isLoading ? <StatusBanner tone="loading" title="載入中">正在整理工作台資料...</StatusBanner> : null}
        {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

        {query.data ? (
          <>
            <div className="module-flow">
              <div className="module-step">
                <div className="module-step-label">先看什麼</div>
                <div className="dashboard-focus">
                  <div>
                    <span className="dashboard-focus-label">開工提示</span>
                    <strong>{focusCopy}</strong>
                  </div>
                  <span className="pill">{todayLabel()}</span>
                </div>

                <div className="dashboard-strip">
                  {cards.map((card) => (
                    <div className="dashboard-metric" key={card.label}>
                      <span>{card.label}</span>
                      <strong>{card.value}</strong>
                    </div>
                  ))}
                </div>
              </div>

              <div className="module-step">
                <div className="module-step-label">在哪裡操作</div>
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
                  <button className="action-choice-card" type="button" onClick={() => onNavigate("sales")}>
                    <span className="action-choice-kicker">收尾更新</span>
                    <strong>POS 匯入</strong>
                    <span className="action-choice-meta">同步今天銷售資料</span>
                  </button>
                </div>
              </div>

              <div className="module-step">
                <div className="module-step-label">結果在哪裡看</div>
                <div className="split-grid dashboard-grid">
              <section className="table-card split-card">
                <div className="split-card-header">
                  <strong>今天先處理</strong>
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
                  <div className="empty-state dashboard-empty-state">目前沒有低庫存原料，今天暫時不需要優先補貨。</div>
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

              <section className="table-card split-card">
                <div className="split-card-header">
                  <strong>今天已完成</strong>
                  <div className="toolbar-actions">
                    <button className="table-link" type="button" onClick={() => onNavigate("production")}>
                      去產品生產
                    </button>
                    <button className="table-link" type="button" onClick={() => onNavigate("reports")}>
                      看報表
                    </button>
                  </div>
                </div>
                {recentActivities.length === 0 ? (
                  <div className="empty-state dashboard-empty-state">今天還沒有新的入庫或生產活動。</div>
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
                </div>
              </div>
            </div>
          </>
        ) : null}
      </section>
    </>
  );
}
