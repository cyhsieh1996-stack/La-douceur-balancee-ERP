import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExampleBanner } from "../../components/ExampleBanner";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type { SalesImportPayload, SalesImportResponse, SalesResponse } from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, "");
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

type SalesPageProps = {
  onNavigate: (moduleId: "reports" | "overview" | "inventory") => void;
};

export function SalesPage({ onNavigate }: SalesPageProps) {
  const queryClient = useQueryClient();
  const [rawText, setRawText] = useState("");
  const [previewSummary, setPreviewSummary] = useState<{
    totalRows: number;
    totalAmount: number;
    firstProduct: string | null;
  } | null>(null);

  const query = useQuery({
    queryKey: ["sales-records"],
    queryFn: () => apiFetch<SalesResponse>("/api/sales"),
  });

  const importMutation = useMutation({
    mutationFn: (payload: SalesImportPayload) =>
      apiFetch<SalesImportResponse>("/api/sales/import", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["sales-records"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setRawText("");
      setPreviewSummary(null);
    },
  });

  function parseRows() {
    const lines = rawText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    return lines.map((line, index) => {
      const parts = line.includes("\t") ? line.split("\t") : line.split(",");
      const [saleDate, productName, qty, price, amount, orderId] = parts.map((part) => part.trim());
      if (!productName || !qty || !amount) {
        throw new Error(`第 ${index + 1} 行格式錯誤，至少需要：日期, 品名, 數量, 單價, 金額, 單號`);
      }

      return {
        saleDate: saleDate || null,
        productName,
        qty: Number(qty),
        price: Number(price || 0),
        amount: Number(amount),
        orderId: orderId || null,
      };
    });
  }

  function handleImport() {
    importMutation.reset();
    const rows = parseRows();
    importMutation.mutate({ rows });
  }

  function handlePreview() {
    importMutation.reset();
    const rows = parseRows();
    setPreviewSummary({
      totalRows: rows.length,
      totalAmount: rows.reduce((total, row) => total + row.amount, 0),
      firstProduct: rows[0]?.productName ?? null,
    });
  }

  const canPreviewOrImport = rawText.trim() !== "";

  return (
    <section className="section">
      <div className="section-title">
        <h2>POS / 銷售匯入</h2>
        <p>先支援貼上 CSV 或 Tab 分隔資料，把銷售資料寫入系統，後續再補檔案上傳與欄位對應精靈。</p>
      </div>

      <ExampleBanner>
        例如：`2026-03-26,檸檬塔,2,160,320,POS-001` 或 `2026-03-26,草莓鮮奶油蛋糕,1,980,980,POS-002`。
      </ExampleBanner>

      <div className="toolbar-card">
        <div className="toolbar-copy">
          <strong>目前進度</strong>
          <p>已接好 `/api/sales` 與 `/api/sales/import`，匯入後會同步更新工作台的今日銷售與月銷售。</p>
        </div>
        <div className="toolbar-actions">
          <span className="pill">Sales Ready</span>
          <span className="pill">最近紀錄 {query.data?.items.length ?? 0} 筆</span>
        </div>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>貼上銷售報表</strong>
            <p>每行一筆：日期, 品名, 數量, 單價, 金額, 單號。也支援 Tab 分隔。</p>
          </div>
          <span className="pill">CSV / TSV</span>
        </div>

        <label className="field">
          <span>銷售內容</span>
          <textarea
            className="paste-box"
            value={rawText}
            onChange={(event) => setRawText(event.target.value)}
            placeholder={"2026-03-26,檸檬塔,2,160,320,POS-001\n2026-03-26,草莓鮮奶油蛋糕,1,980,980,POS-002"}
          />
        </label>

        <div className="form-actions">
          <button className="secondary-button" type="button" onClick={handlePreview} disabled={!canPreviewOrImport}>
            預覽匯入
          </button>
          <button className="primary-button" type="button" onClick={handleImport} disabled={!canPreviewOrImport || importMutation.isPending}>
            {importMutation.isPending ? "匯入中..." : "匯入銷售資料"}
          </button>
          {!canPreviewOrImport ? <span className="form-hint">先貼上 CSV 或 Tab 分隔內容，才能預覽或匯入。</span> : null}
        </div>

        {previewSummary ? (
          <StatusBanner title="預覽結果">
            共 {previewSummary.totalRows} 筆，總金額 ${formatNumber(previewSummary.totalAmount)}
            {previewSummary.firstProduct ? `，第一筆產品：${previewSummary.firstProduct}` : ""}
          </StatusBanner>
        ) : null}
        {importMutation.isError ? <StatusBanner tone="error" title="匯入失敗">{String(importMutation.error)}</StatusBanner> : null}
        {importMutation.isSuccess ? (
          <>
            <StatusBanner tone="success" title="匯入完成">已成功匯入 {importMutation.data.importedCount} 筆銷售資料。</StatusBanner>
            <div className="flow-actions">
              <button className="secondary-button" type="button" onClick={() => onNavigate("reports")}>
                下一步：查看報表
              </button>
              <button className="secondary-button" type="button" onClick={() => onNavigate("inventory")}>
                查看庫存中心
              </button>
              <button className="table-link" type="button" onClick={() => onNavigate("overview")}>
                回今日作業
              </button>
            </div>
          </>
        ) : null}
      </div>

      {query.isLoading ? <div className="empty-state">正在載入銷售紀錄...</div> : null}
      {query.isError ? <StatusBanner tone="error" title="載入失敗">{String(query.error)}</StatusBanner> : null}

      {query.data ? (
        <section className="table-card split-card">
          <div className="split-card-header">
            <strong>最近銷售紀錄</strong>
            <span className="pill">{query.data.source} / {query.data.items.length} 筆</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>單號</th>
                <th>產品</th>
                <th>數量</th>
                <th>單價</th>
                <th>金額</th>
              </tr>
            </thead>
            <tbody>
              {query.data.items.map((item) => (
                <tr key={item.id}>
                  <td>{formatDate(item.date)}</td>
                  <td>{item.orderId || "-"}</td>
                  <td>{item.productName}</td>
                  <td>{formatNumber(item.qty)}</td>
                  <td>${formatNumber(item.price)}</td>
                  <td>${formatNumber(item.amount)}</td>
                </tr>
              ))}
              {query.data.items.length === 0 ? (
                <tr className="table-row-example">
                  <td className="table-empty-cell" colSpan={6}>
                    範例：2026-03-26 / POS-001 / 檸檬塔 / 2 / $160 / $320
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </section>
      ) : null}
    </section>
  );
}
