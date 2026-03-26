import { useMemo, useState } from "react";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { InboundPage } from "./features/inbound/InboundPage";
import { InventoryPage } from "./features/inventory/InventoryPage";
import { MaterialsPage } from "./features/materials/MaterialsPage";
import { ProductionPage } from "./features/production/ProductionPage";
import { ProductsPage } from "./features/products/ProductsPage";
import { ReportsPage } from "./features/reports/ReportsPage";
import { SalesPage } from "./features/sales/SalesPage";

type ModuleId =
  | "overview"
  | "inbound"
  | "production"
  | "sales"
  | "inventory"
  | "materials"
  | "products"
  | "reports";

type PrimaryView = "today" | "operations" | "masters" | "reports";

const operationsTabs = [
  { id: "inbound", title: "入庫" },
  { id: "production", title: "生產" },
  { id: "sales", title: "銷售" },
  { id: "inventory", title: "庫存" },
] as const;

const masterTabs = [
  { id: "materials", title: "原料" },
  { id: "products", title: "產品與配方" },
] as const;

function getPrimaryView(moduleId: ModuleId): PrimaryView {
  if (moduleId === "overview") return "today";
  if (moduleId === "reports") return "reports";
  if (["materials", "products"].includes(moduleId)) return "masters";
  return "operations";
}

export function App() {
  const [activeModule, setActiveModule] = useState<ModuleId>("overview");
  const activePrimary = getPrimaryView(activeModule);

  const headerMeta = useMemo(() => {
    switch (activePrimary) {
      case "today":
        return {
          title: "今日作業",
          desc: "先看今天一定要先處理的事，再決定補貨、生產或整理銷售。",
        };
      case "operations":
        return {
          title: "作業流程",
          desc: "把入庫、生產、銷售和庫存放在同一區，照工作順序往下做。",
        };
      case "masters":
        return {
          title: "主檔設定",
          desc: "需要維護原料、產品和配方時再進來，不和日常作業混在一起。",
        };
      case "reports":
        return {
          title: "報表摘要",
          desc: "集中看銷售、支出、低庫存和熱銷產品，不把分析塞進作業頁。",
        };
    }
  }, [activePrimary]);

  return (
    <main className="app-shell app-shell-simple">
      <header className="app-header">
        <div>
          <p className="eyebrow">La Douceur Balancee ERP</p>
          <h1 className="app-title">{headerMeta.title}</h1>
          <p className="app-subtitle">{headerMeta.desc}</p>
        </div>
        <span className="status-label">Web 版營運中</span>
      </header>

      <nav className="primary-nav" aria-label="primary sections">
        <button
          className={activePrimary === "today" ? "primary-nav-tab active" : "primary-nav-tab"}
          type="button"
          onClick={() => setActiveModule("overview")}
        >
          今日作業
        </button>
        <button
          className={activePrimary === "operations" ? "primary-nav-tab active" : "primary-nav-tab"}
          type="button"
          onClick={() => setActiveModule("inbound")}
        >
          作業流程
        </button>
        <button
          className={activePrimary === "masters" ? "primary-nav-tab active" : "primary-nav-tab"}
          type="button"
          onClick={() => setActiveModule("materials")}
        >
          主檔設定
        </button>
        <button
          className={activePrimary === "reports" ? "primary-nav-tab active" : "primary-nav-tab"}
          type="button"
          onClick={() => setActiveModule("reports")}
        >
          報表摘要
        </button>
      </nav>

      {activePrimary === "operations" ? (
        <nav className="secondary-nav" aria-label="operations tabs">
          {operationsTabs.map((tab) => (
            <button
              key={tab.id}
              className={activeModule === tab.id ? "secondary-nav-tab active" : "secondary-nav-tab"}
              type="button"
              onClick={() => setActiveModule(tab.id)}
            >
              {tab.title}
            </button>
          ))}
        </nav>
      ) : null}

      {activePrimary === "masters" ? (
        <nav className="secondary-nav" aria-label="master tabs">
          {masterTabs.map((tab) => (
            <button
              key={tab.id}
              className={activeModule === tab.id ? "secondary-nav-tab active" : "secondary-nav-tab"}
              type="button"
              onClick={() => setActiveModule(tab.id)}
            >
              {tab.title}
            </button>
          ))}
        </nav>
      ) : null}

      {activeModule === "overview" ? <DashboardPage onNavigate={setActiveModule} /> : null}
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
