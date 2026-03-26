import { useMemo, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExampleBanner } from "../../components/ExampleBanner";
import { StatusBanner } from "../../components/StatusBanner";
import { apiFetch } from "../../lib/api";
import type { MaterialsResponse } from "../materials/types";
import type { CreateInboundPayload, CreateInboundResponse, InboundResponse } from "./types";

function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(3).replace(/\.?0+$/, "");
}

function formatMoney(value: number) {
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function formatDate(value: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function todayString() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

type InboundPageProps = {
  onNavigate: (moduleId: "production" | "inventory" | "overview") => void;
};

export function InboundPage({ onNavigate }: InboundPageProps) {
  const queryClient = useQueryClient();
  const [materialId, setMaterialId] = useState("");
  const [qty, setQty] = useState("");
  const [unitPrice, setUnitPrice] = useState("");
  const [batchNumber, setBatchNumber] = useState("");
  const [expiryDate, setExpiryDate] = useState(todayString());
  const [note, setNote] = useState("");

  const materialsQuery = useQuery({
    queryKey: ["materials-for-inbound"],
    queryFn: () => apiFetch<MaterialsResponse>("/api/materials"),
  });

  const inboundQuery = useQuery({
    queryKey: ["inbound-records"],
    queryFn: () => apiFetch<InboundResponse>("/api/inbound"),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateInboundPayload) =>
      apiFetch<CreateInboundResponse>("/api/inbound", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["inbound-records"] });
      await queryClient.invalidateQueries({ queryKey: ["materials"] });
      await queryClient.invalidateQueries({ queryKey: ["materials-for-inbound"] });
      await queryClient.invalidateQueries({ queryKey: ["inventory-center"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setQty("");
      setUnitPrice("");
      setBatchNumber("");
      setNote("");
    },
  });

  const selectedMaterial = useMemo(
    () => materialsQuery.data?.items.find((item) => String(item.id) === materialId) ?? null,
    [materialsQuery.data, materialId],
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createMutation.reset();
    createMutation.mutate({
      materialId: Number(materialId),
      qty: Number(qty),
      unitPrice: unitPrice === "" ? 0 : Number(unitPrice),
      batchNumber: batchNumber.trim() || null,
      expiryDate: expiryDate || null,
      note: note.trim() || null,
    });
  }

  const canSubmit = materialId !== "" && qty !== "" && Number(qty) > 0;

  return (
    <section className="section">
      <div className="section-title">
        <h2>進貨與入庫</h2>
        <p>沿用桌面版的入庫流程，寫入紀錄後同步更新原料庫存與參考單價。</p>
      </div>

      <ExampleBanner>
        例如：低筋麵粉入庫 `10 kg`、單價 `52`、批號 `FLOUR-20260326`、效期填 `2026-04-30`。
      </ExampleBanner>

      <div className="toolbar-card">
        <div className="toolbar-copy">
          <strong>今日入庫</strong>
          <p>先把今天要用的原料補齊，後面生產和庫存會一起更新。</p>
        </div>
        <div className="toolbar-actions">
          <span className="pill">Inbound Ready</span>
          <span className="pill">最近紀錄 {inboundQuery.data?.items.length ?? 0} 筆</span>
        </div>
      </div>

      <div className="form-card">
        <div className="form-card-header">
          <div>
            <strong>新增入庫</strong>
            <p>填寫進貨數量、單價、批號與效期，儲存後系統會直接增加原料庫存。</p>
          </div>
          {selectedMaterial ? (
            <div className="info-row compact">
              <span>目前庫存：{formatNumber(selectedMaterial.stock)} {selectedMaterial.unit ?? ""}</span>
              <span>參考單價：${formatMoney(selectedMaterial.unitPrice)}</span>
            </div>
          ) : null}
        </div>

        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="field">
            <span>原料</span>
            <select value={materialId} onChange={(event) => setMaterialId(event.target.value)}>
              <option value="">選擇原料</option>
              {materialsQuery.data?.items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>入庫數量</span>
            <input
              type="number"
              min="0"
              step="0.001"
              value={qty}
              onChange={(event) => setQty(event.target.value)}
              placeholder="例如：10"
            />
          </label>

          <label className="field">
            <span>進貨單價</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={unitPrice}
              onChange={(event) => setUnitPrice(event.target.value)}
              placeholder="可留空"
            />
          </label>

          <label className="field">
            <span>批號</span>
            <input value={batchNumber} onChange={(event) => setBatchNumber(event.target.value)} placeholder="選填" />
          </label>

          <label className="field">
            <span>有效期限</span>
            <input type="date" value={expiryDate} onChange={(event) => setExpiryDate(event.target.value)} />
          </label>

          <label className="field field-span-2">
            <span>備註</span>
            <input value={note} onChange={(event) => setNote(event.target.value)} placeholder="例如：促銷進貨、緊急補貨" />
          </label>

          <div className="form-actions">
            <button className="primary-button" type="submit" disabled={!canSubmit || createMutation.isPending}>
              {createMutation.isPending ? "入庫中..." : "確認入庫"}
            </button>
            {!canSubmit ? <span className="form-hint">請先選原料並輸入大於 0 的入庫數量。</span> : null}
          </div>
        </form>

        {createMutation.isError ? <StatusBanner tone="error" title="入庫失敗">{String(createMutation.error)}</StatusBanner> : null}
        {createMutation.isSuccess ? (
          <>
            <StatusBanner tone="success" title="入庫完成">原料、庫存中心與工作台摘要都已更新。</StatusBanner>
            <div className="flow-actions">
              <button className="secondary-button" type="button" onClick={() => onNavigate("production")}>
                下一步：前往生產
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

      {inboundQuery.isLoading ? <div className="empty-state">正在載入最近入庫紀錄...</div> : null}
      {inboundQuery.isError ? <StatusBanner tone="error" title="載入失敗">{String(inboundQuery.error)}</StatusBanner> : null}

      {inboundQuery.data ? (
        <section className="table-card split-card">
          <div className="split-card-header">
            <strong>最近入庫紀錄</strong>
            <span className="pill">{inboundQuery.data.source} / {inboundQuery.data.items.length} 筆</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>原料</th>
                <th>數量</th>
                <th>單價</th>
                <th>批號</th>
                <th>有效期限</th>
              </tr>
            </thead>
            <tbody>
              {inboundQuery.data.items.map((item) => (
                <tr key={item.id}>
                  <td>{formatDate(item.date)}</td>
                  <td>{item.materialName}</td>
                  <td>
                    {formatNumber(item.qty)} {item.unit ?? ""}
                  </td>
                  <td>${formatMoney(item.unitPrice)}</td>
                  <td>{item.batchNumber || "-"}</td>
                  <td>{formatDate(item.expiryDate)}</td>
                </tr>
              ))}
              {inboundQuery.data.items.length === 0 ? (
                <tr className="table-row-example">
                  <td className="table-empty-cell" colSpan={6}>
                    範例：2026-03-26 / 低筋麵粉 / 10 kg / $52 / FLOUR-20260326 / 2026-04-30
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
