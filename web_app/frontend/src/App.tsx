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
  { id: "materials", title: "原料主檔", desc: "維護原料、供應商與安全庫存" },
  { id: "products", title: "產品與配方", desc: "維護售價、保存期與 BOM 配方" },
  { id: "inbound", title: "進貨與入庫", desc: "建立進貨紀錄並同步更新庫存" },
  { id: "production", title: "生產與批號", desc: "建立批次並依配方自動扣料" },
  { id: "inventory", title: "庫存中心", desc: "看即時庫存、低庫存與盤點異動" },
  { id: "sales", title: "POS 匯入", desc: "匯入銷售報表並更新工作台" },
  { id: "reports", title: "報表與摘要", desc: "看本月銷售、入庫支出與熱銷產品" },
 ] as const;

const apiModules = [
  "/api/dashboard",
  "/api/materials",
  "/api/products",
  "/api/recipes",
  "/api/inbound",
  "/api/production",
  "/api/inventory",
  "/api/sales",
  "/api/reports",
];

const webModules = [
  { id: "overview", title: "今日作業" },
  { id: "materials", title: "原料主檔" },
  { id: "products", title: "產品主檔" },
  { id: "inbound", title: "進貨與入庫" },
  { id: "production", title: "生產與批號" },
  { id: "inventory", title: "庫存中心" },
  { id: "sales", title: "POS / 銷售" },
  { id: "reports", title: "報表 / 摘要" },
 ] as const;

type ModuleId = (typeof webModules)[number]["id"];

export function App() {
  const [activeModule, setActiveModule] = useState<ModuleId>("overview");

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Web ERP Migration</p>
          <h1>La Douceur Balancee ERP</h1>
          <p className="hero-copy">
            現在已經把主檔、入庫、生產、庫存與銷售流程接上。接下來會繼續把互動細節、報表與權限整理到可正式上線的程度。
          </p>
        </div>
        <div className="status-card">
          <span className="status-label">目前狀態</span>
          <strong>核心流程已打通</strong>
          <p>下一步：收斂搜尋、空狀態、錯誤提示與報表 / 權限等商用細節。</p>
        </div>
      </section>

      <nav className="module-tabs" aria-label="web modules">
        {webModules.map((module) => (
          <button
            key={module.id}
            className={module.id === activeModule ? "module-tab active" : "module-tab"}
            onClick={() => setActiveModule(module.id)}
            type="button"
          >
            {module.title}
          </button>
        ))}
      </nav>

      {activeModule === "overview" ? (
        <>
          <DashboardPage onNavigate={setActiveModule} />

          <section className="section">
            <div className="section-title">
              <h2>快捷作業</h2>
              <p>從工作台直接跳到常用模組，不用先在腦中重新找路徑。</p>
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

          <section className="section">
            <div className="section-title">
              <h2>API 模組規劃</h2>
              <p>Cloudflare Worker 會承接交易規則，不讓前端直接改庫存。</p>
            </div>
            <div className="api-list">
              {apiModules.map((module) => (
                <code key={module}>{module}</code>
              ))}
            </div>
          </section>
        </>
      ) : null}

      {activeModule === "materials" ? <MaterialsPage /> : null}
      {activeModule === "products" ? <ProductsPage /> : null}
      {activeModule === "inbound" ? <InboundPage /> : null}
      {activeModule === "production" ? <ProductionPage /> : null}
      {activeModule === "inventory" ? <InventoryPage /> : null}
      {activeModule === "sales" ? <SalesPage /> : null}
      {activeModule === "reports" ? <ReportsPage /> : null}
    </main>
  );
}
