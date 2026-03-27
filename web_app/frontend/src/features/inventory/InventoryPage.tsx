import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type {
  InventoryAdjustmentPayload,
  InventoryAdjustmentResponse,
  InventoryCenterResponse,
  InventoryItem,
} from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

function formatMoney(value: number) {
  return `$${value.toFixed(2).replace(/\.?0+$/, "")}`;
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export function InventoryPage() {
  const queryClient = useQueryClient();
  const [keyword, setKeyword] = useState("");
  const [searchKeyword, setSearchKeyword] = useState("");
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [actualStock, setActualStock] = useState("");
  const [reason, setReason] = useState("");

  const query = useQuery({
    queryKey: ["inventory-center", searchKeyword, lowStockOnly],
    queryFn: () =>
      apiFetch<InventoryCenterResponse>(
        `/api/inventory?keyword=${encodeURIComponent(searchKeyword)}&lowStockOnly=${String(lowStockOnly)}`,
      ),
  });

  const adjustMutation = useMutation({
    mutationFn: (payload: InventoryAdjustmentPayload) =>
      apiFetch<InventoryAdjustmentResponse>("/api/inventory/adjustments", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["inventory-center"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setActualStock("");
      setReason("");
    },
  });

  const cards = useMemo(() => {
    if (!query.data) return [];
    return [
      { label: "原料總數", value: query.data.summary.materialCount, hint: "主檔總筆數" },
      { label: "低庫存", value: query.data.summary.lowStockCount, hint: "低於安全庫存" },
      { label: "零庫存", value: query.data.summary.zeroStockCount, hint: "需要確認是否停用或補貨" },
      { label: "估算庫存值", value: formatMoney(query.data.summary.estimatedStockValue), hint: "依單價估算" },
    ];
  }, [query.data]);

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearchKeyword(keyword.trim());
  }

  function handleSelectItem(item: InventoryItem) {
    setSelectedItem(item);
    setActualStock(String(item.stock));
  }

  function handleAdjustmentSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedItem) return;
    adjustMutation.reset();
    adjustMutation.mutate({
      materialId: selectedItem.id,
      newStock: Number(actualStock),
      reason: reason.trim() || null,
    });
  }

  return (
    <section className="section">
      <div className="section-title">
        <h2>庫存中心</h2>
        <p>集中看即時庫存、低庫存提醒、盤點調整與最近異動。</p>
      </div>

      {query.isLoading ? <div className="empty-state">正在整理庫存資料...</div> : null}
      {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

      {query.data ? (
        <div className="module-flow">
          <div className="module-step">
            <div className="module-step-label">先看什麼</div>
            <div className="workflow-strip">
              <div className="workflow-strip-copy">
                <strong>先確認庫存風險</strong>
                <div className="workflow-steps">
                  <span className="step-chip"><span className="step-chip-index">1</span>看低庫存</span>
                  <span className="step-chip"><span className="step-chip-index">2</span>找零庫存</span>
                  <span className="step-chip"><span className="step-chip-index">3</span>決定是否盤點</span>
                </div>
              </div>
              <div className="strip-meta">
                <span>資料來源 {query.data.source}</span>
                <span>顯示 {query.data.items.length} 筆</span>
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
            <div className="module-step-label">在哪裡操作</div>
            <div className="filter-toolbar">
              <div className="filter-toolbar-main">
                <strong>先找原料，再盤點調整</strong>
                <div className="filter-toolbar-form">
                  <input
                    value={keyword}
                    onChange={(event) => setKeyword(event.target.value)}
                    placeholder="搜尋名稱、類別、廠商、廠牌"
                  />
                  <label className="checkbox-field">
                    <input
                      type="checkbox"
                      checked={lowStockOnly}
                      onChange={(event) => setLowStockOnly(event.target.checked)}
                    />
                    <span>只看低庫存</span>
                  </label>
                  <button className="primary-button" type="submit" form="inventory-search-form">
                    搜尋
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => {
                      setKeyword("");
                      setSearchKeyword("");
                      setLowStockOnly(false);
                    }}
                  >
                    清除
                  </button>
                </div>
              </div>
              <div className="filter-toolbar-meta">
                <strong>可直接從清單帶入盤點</strong>
                <p>目前顯示 {query.data.items.length} 筆原料</p>
              </div>
            </div>
            <form id="inventory-search-form" className="visually-hidden" onSubmit={handleSearchSubmit} />

            <div className="split-grid inventory-layout">
            <section className="table-card split-card">
              <div className="split-card-header">
                <strong>即時庫存</strong>
                <span className="pill">點選列可帶入盤點</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>原料</th>
                    <th>類別</th>
                    <th>廠商</th>
                    <th>庫存</th>
                    <th>安全庫存</th>
                    <th>距安全量</th>
                  </tr>
                </thead>
                <tbody>
                  {query.data.items.map((item) => (
                    <tr
                      key={item.id}
                      data-state={item.isLowStock ? "warning" : "normal"}
                      data-selected={selectedItem?.id === item.id ? "true" : "false"}
                      onClick={() => handleSelectItem(item)}
                    >
                      <td>{item.name}</td>
                      <td>{item.category || "-"}</td>
                      <td>{item.vendor || "-"}</td>
                      <td>
                        {formatNumber(item.stock)} {item.unit ?? ""}
                      </td>
                      <td>
                        {formatNumber(item.safeStock)} {item.unit ?? ""}
                      </td>
                      <td>{formatNumber(item.balanceToSafe)}</td>
                    </tr>
                  ))}
                  {query.data.items.length === 0 ? (
                    <tr>
                      <td className="table-empty-cell" colSpan={6}>
                        沒有符合目前搜尋條件的原料，請調整關鍵字或取消低庫存篩選。
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </section>

            <section className="form-card split-card">
              <div className="split-card-header">
                <strong>盤點調整</strong>
                <span className="pill">{selectedItem ? "Ready" : "Select a row"}</span>
              </div>
              <form className="form-grid compact-form" onSubmit={handleAdjustmentSubmit}>
                <label className="field">
                  <span>原料</span>
                  <input value={selectedItem?.name ?? ""} readOnly placeholder="從左側清單選一筆" />
                </label>
                <label className="field">
                  <span>目前庫存</span>
                  <input
                    value={
                      selectedItem ? `${formatNumber(selectedItem.stock)} ${selectedItem.unit ?? ""}`.trim() : ""
                    }
                    readOnly
                  />
                </label>
                <label className="field">
                  <span>實際盤點數量</span>
                  <input
                    type="number"
                    inputMode="numeric"
                    min="0"
                    step="1"
                    value={actualStock}
                    onChange={(event) => setActualStock(event.target.value)}
                    placeholder="輸入盤點後數量"
                    disabled={!selectedItem}
                  />
                </label>
                <label className="field field-span-2">
                  <span>調整原因</span>
                  <input
                    value={reason}
                    onChange={(event) => setReason(event.target.value)}
                    placeholder="例如：盤點差異、破損、過期報廢"
                    disabled={!selectedItem}
                  />
                </label>
                <div className="form-actions">
                  <button className="primary-button" type="submit" disabled={!selectedItem || adjustMutation.isPending}>
                    {adjustMutation.isPending ? "調整中..." : "確認調整"}
                  </button>
                </div>
              </form>
              {!selectedItem ? <div className="empty-state">從左側即時庫存清單點一筆原料，就能直接帶入盤點調整。</div> : null}
              {adjustMutation.isError ? <StatusBanner tone="error" title="調整失敗">{String(adjustMutation.error)}</StatusBanner> : null}
              {adjustMutation.isSuccess ? <StatusBanner tone="success" title="調整完成">庫存與最近異動已同步更新。</StatusBanner> : null}
            </section>
          </div>
          </div>

          <div className="module-step">
            <div className="module-step-label">結果在哪裡看</div>
            <section className="table-card split-card">
            <div className="split-card-header">
              <strong>最近異動</strong>
              <span className="pill">{query.data.recentAdjustments.length} 筆</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>原料</th>
                  <th>原本庫存</th>
                  <th>盤點後</th>
                  <th>增減量</th>
                  <th>原因</th>
                </tr>
              </thead>
              <tbody>
                {query.data.recentAdjustments.map((item) => (
                  <tr key={item.id}>
                    <td>{formatDate(item.date)}</td>
                    <td>{item.materialName}</td>
                    <td>
                      {formatNumber(item.oldStock)} {item.unit ?? ""}
                    </td>
                    <td>
                      {formatNumber(item.newStock)} {item.unit ?? ""}
                    </td>
                    <td>{formatNumber(item.diff)}</td>
                    <td>{item.reason || "-"}</td>
                  </tr>
                ))}
                {query.data.recentAdjustments.length === 0 ? (
                  <tr>
                    <td className="table-empty-cell" colSpan={6}>
                      目前還沒有盤點異動紀錄，做完第一筆調整後會顯示在這裡。
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
