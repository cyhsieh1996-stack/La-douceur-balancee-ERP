import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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

export function SalesPage() {
  const queryClient = useQueryClient();
  const [rawText, setRawText] = useState("");

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

  return (
    <section className="section">
      <div className="section-title">
        <h2>POS / 銷售匯入</h2>
        <p>先支援貼上 CSV 或 Tab 分隔資料，把銷售資料寫入系統，後續再補檔案上傳與欄位對應精靈。</p>
      </div>

      <div className="toolbar-card">
        <div>
          <strong>目前進度</strong>
          <p>已接好 `/api/sales` 與 `/api/sales/import`，匯入後會同步更新工作台的今日銷售與月銷售。</p>
        </div>
        <span className="pill">Sales Ready</span>
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
          <button className="primary-button" type="button" onClick={handleImport} disabled={importMutation.isPending}>
            {importMutation.isPending ? "匯入中..." : "匯入銷售資料"}
          </button>
        </div>

        {importMutation.isError ? <div className="empty-state error">匯入失敗：{String(importMutation.error)}</div> : null}
        {importMutation.isSuccess ? (
          <div className="empty-state success">已成功匯入 {importMutation.data.importedCount} 筆銷售資料。</div>
        ) : null}
      </div>

      {query.isLoading ? <div className="empty-state">正在載入銷售紀錄...</div> : null}
      {query.isError ? <div className="empty-state error">載入失敗：{String(query.error)}</div> : null}

      {query.data ? (
        <section className="table-card split-card">
          <div className="split-card-header">
            <strong>最近銷售紀錄</strong>
            <span className="pill">{query.data.items.length} 筆</span>
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
            </tbody>
          </table>
        </section>
      ) : null}
    </section>
  );
}
