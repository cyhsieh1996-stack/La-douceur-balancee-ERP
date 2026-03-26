import { useState } from "react";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { InboundPage } from "./features/inbound/InboundPage";
import { InventoryPage } from "./features/inventory/InventoryPage";
import { MaterialsPage } from "./features/materials/MaterialsPage";
import { ProductionPage } from "./features/production/ProductionPage";
import { ProductsPage } from "./features/products/ProductsPage";
import { ReportsPage } from "./features/reports/ReportsPage";
import { SalesPage } from "./features/sales/SalesPage";

const quickActions = [
  { id: "inbound", title: "進貨與入庫", desc: "建立進貨紀錄並同步更新庫存" },
  { id: "production", title: "生產與批號", desc: "建立批次並依配方自動扣料" },
  { id: "sales", title: "POS 匯入", desc: "匯入銷售報表並更新工作台" },
  { id: "inventory", title: "庫存中心", desc: "看即時庫存、低庫存與盤點異動" },
  { id: "reports", title: "報表與摘要", desc: "看本月銷售、入庫支出與熱銷產品" },
  { id: "materials", title: "原料主檔", desc: "維護原料、供應商與安全庫存" },
  { id: "products", title: "產品與配方", desc: "維護售價、保存期與 BOM 配方" },
] as const;

const webModules = [
  { id: "overview", title: "今日作業" },
  { id: "inbound", title: "進貨與入庫" },
  { id: "production", title: "生產與批號" },
  { id: "sales", title: "POS / 銷售" },
  { id: "inventory", title: "庫存中心" },
  { id: "reports", title: "報表 / 摘要" },
  { id: "materials", title: "原料主檔" },
  { id: "products", title: "產品主檔" },
] as const;

type ModuleId = (typeof webModules)[number]["id"];

const moduleGroups: Array<{
  label: string;
  modules: Array<(typeof webModules)[number]>;
}> = [
  {
    label: "日常作業",
    modules: webModules.filter((module) =>
      ["overview", "inbound", "production", "sales", "inventory", "reports"].includes(module.id),
    ),
  },
  {
    label: "主檔設定",
    modules: webModules.filter((module) => ["materials", "products"].includes(module.id)),
  },
];

export function App() {
  const [activeModule, setActiveModule] = useState<ModuleId>("overview");

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div className="hero-copy-block">
          <p className="eyebrow">Web ERP Migration</p>
          <h1>La Douceur Balancee ERP</h1>
          <p className="hero-copy">
            現在已經把主檔、入庫、生產、庫存與銷售流程接上。接下來會繼續把互動細節、報表與權限整理到可正式上線的程度。
          </p>
          <div className="hero-meta">
            <span className="hero-badge">Cloudflare Pages</span>
            <span className="hero-badge">Workers API</span>
            <span className="hero-badge">Supabase</span>
          </div>
        </div>
        <div className="status-card">
          <span className="status-label">目前狀態</span>
          <strong>核心流程已打通</strong>
          <p>下一步：收斂搜尋、空狀態、錯誤提示與報表 / 權限等商用細節。</p>
        </div>
      </section>

      <section className="workflow-nav" aria-label="web modules">
        {moduleGroups.map((group) => (
          <div className="workflow-group" key={group.label}>
            <span className="workflow-label">{group.label}</span>
            <div className="module-tabs">
              {group.modules.map((module) => (
                <button
                  key={module.id}
                  className={module.id === activeModule ? "module-tab active" : "module-tab"}
                  onClick={() => setActiveModule(module.id)}
                  type="button"
                >
                  {module.title}
                </button>
              ))}
            </div>
          </div>
        ))}
      </section>

      {activeModule === "overview" ? (
        <>
          <DashboardPage onNavigate={setActiveModule} />

          <section className="section">
            <div className="section-title">
              <h2>今日建議流程</h2>
              <p>先處理入庫與生產，再回看銷售、庫存與報表，主檔設定放在後面維護。</p>
            </div>
            <div className="grid shortcut-grid">
              {quickActions.map((item) => (
                <article className="panel shortcut-card" key={item.title}>
                  <h3>{item.title}</h3>
                  <p>{item.desc}</p>
                  <button className="secondary-button shortcut-button" type="button" onClick={() => setActiveModule(item.id)}>
                    前往 {item.title}
                  </button>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}

      {activeModule === "materials" ? <MaterialsPage /> : null}
      {activeModule === "products" ? <ProductsPage /> : null}
      {activeModule === "inbound" ? <InboundPage onNavigate={setActiveModule} /> : null}
      {activeModule === "production" ? <ProductionPage onNavigate={setActiveModule} /> : null}
      {activeModule === "inventory" ? <InventoryPage /> : null}
      {activeModule === "sales" ? <SalesPage onNavigate={setActiveModule} /> : null}
      {activeModule === "reports" ? <ReportsPage /> : null}
    </main>
  );
}
