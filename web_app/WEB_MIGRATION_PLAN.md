# La Douceur Balancee ERP Web Migration Plan

## 1. Goal

將目前的 `customtkinter` 桌面 ERP 重構為：

- 前端：Cloudflare Pages 上的 Web UI
- API / 業務層：Cloudflare Workers
- 資料庫 / 驗證 / 檔案：Supabase

這不是單純部署，而是將目前桌面版的 UI、邏輯與資料層拆開，改成可多人使用、可登入、可擴充的 Web ERP。

## 2. Current Desktop Scope

目前已收斂完成的核心功能：

- 今日作業工作台
- 原料主檔
- 產品主檔
- 產品配方 / BOM
- 原料入庫
- 生產登錄
- POS 匯入
- 庫存中心
- 庫存調整紀錄

目前桌面版資料模型：

- `raw_materials`
- `products`
- `product_recipes`
- `inbound_records`
- `production_logs`
- `sales_records`
- `inventory_adjustments`

## 3. Target Architecture

### Frontend

- Cloudflare Pages
- React + TypeScript
- 首頁改為流程型工作台
- 主要頁面：
  - 今日作業
  - 入庫
  - 生產
  - 庫存中心
  - 產品與配方
  - POS 匯入
  - 原料主檔

### Backend

- Cloudflare Workers
- 對外提供 API
- 業務規則集中在 Worker，不放在前端

建議 API 模組：

- `/api/materials`
- `/api/products`
- `/api/recipes`
- `/api/inbound`
- `/api/production`
- `/api/inventory`
- `/api/sales`
- `/api/dashboard`

### Data Layer

- Supabase Postgres
- Supabase Auth
- Supabase Storage
- Supabase Row Level Security

## 4. Why This Split

### Why Supabase

- 很適合承接現在 SQLite 的表結構
- 原生支援 Postgres
- 內建 Auth
- 內建 Storage
- RLS 適合做角色權限
- 後續要做門市、多使用者、稽核紀錄比較順

### Why Cloudflare

- Pages 適合部署 React 前端
- Workers 適合承接輕量 API 與業務流程
- 全球邊緣部署，回應快
- 後續若要接排程、Webhook、匯入任務都方便

## 5. Web Module Mapping

### A. Dashboard / 今日作業

桌面版：

- 工作台摘要卡
- 快捷入口
- 低庫存
- 即期批號
- 最近入庫
- 最近生產

Web 版：

- 保留同樣資訊架構
- 卡片資料改走 `/api/dashboard`
- 表格支援快速跳頁

### B. Raw Materials / 原料主檔

桌面版：

- CRUD
- 搜尋
- 批次貼上

Web 版：

- 列表 + drawer 編輯
- 支援批次 CSV 匯入
- 預留供應商欄位 filter

### C. Products / 產品主檔

桌面版：

- CRUD
- 搜尋
- 批次貼上
- 配方管理

Web 版：

- 產品列表
- 編輯面板
- 配方 / BOM 子頁

### D. Inbound / 入庫

桌面版：

- 原料入庫
- 批號、效期
- 單價回寫

Web 版：

- 表單 + 最近入庫清單
- 後端負責：
  - 新增入庫
  - 增加原料庫存
  - 更新參考單價

### E. Production / 生產

桌面版：

- 批號生成
- 生產登錄
- 自動扣料
- 缺料檢查

Web 版：

- 生產表單
- 配方預覽
- 後端交易處理：
  - 寫入生產紀錄
  - 增加產品庫存
  - 扣除原料庫存
  - 缺料即拒絕交易

### F. Inventory Center / 庫存中心

桌面版：

- 庫存摘要
- 即時庫存表
- 低庫存篩選
- 調整表單
- 異動紀錄

Web 版：

- 維持同樣資訊架構
- 強化 filter / sort / export

### G. POS Import / POS 匯入

桌面版：

- 上傳 Excel / CSV
- 寫入銷售紀錄

Web 版：

- 上傳到 Supabase Storage 或直接 API 處理
- Worker 清洗欄位後寫入 `sales_records`

## 6. Supabase Schema Draft

### raw_materials

- `id`
- `name`
- `category`
- `brand`
- `vendor`
- `unit`
- `unit_price`
- `stock`
- `safe_stock`
- `created_at`
- `updated_at`

### products

- `id`
- `name`
- `category`
- `price`
- `cost`
- `stock`
- `shelf_life`
- `created_at`
- `updated_at`

### product_recipes

- `id`
- `product_id`
- `material_id`
- `qty_per_unit`
- `note`
- `created_at`
- unique `(product_id, material_id)`

### inbound_records

- `id`
- `material_id`
- `qty`
- `unit_price`
- `batch_number`
- `expiry_date`
- `note`
- `created_at`
- `created_by`

### production_logs

- `id`
- `product_id`
- `qty`
- `batch_number`
- `expiry_date`
- `note`
- `created_at`
- `created_by`

### sales_records

- `id`
- `product_name`
- `qty`
- `price`
- `amount`
- `date`
- `order_id`
- `created_at`
- `created_by`

### inventory_adjustments

- `id`
- `material_id`
- `old_stock`
- `new_stock`
- `diff`
- `reason`
- `created_at`
- `created_by`

### profiles

- `id`
- `email`
- `display_name`
- `role`
- `store_id` or `location_id`

建議角色：

- `admin`
- `manager`
- `staff`

## 7. Rules To Keep In Backend

這些規則不要放前端：

- 生產前缺料檢查
- 生產時扣原料
- 入庫時更新參考單價
- 庫存調整寫異動紀錄
- 批號生成規則
- 權限驗證

## 8. RLS Direction

第一版可先做簡單角色權限：

- `admin`：全部可讀寫
- `manager`：大部分可讀寫
- `staff`：可做入庫、生產、POS 匯入、庫存調整，但不能刪主檔

如果未來有多門市，再加：

- `location_id`
- 各資料表增加 `location_id`
- RLS 限制只能看自己門市資料

## 9. Migration Strategy

### Phase 1

先建 Web 專案骨架，不碰正式資料遷移：

- 建立前端專案
- 建立 Worker API 專案
- 建立 Supabase project
- 建立 schema migration

### Phase 2

先做最有價值的流程：

- Auth
- 原料主檔
- 產品主檔
- 配方管理

### Phase 3

- 入庫
- 生產扣料
- 庫存中心

### Phase 4

- POS 匯入
- 今日作業 dashboard
- 權限與操作紀錄

### Phase 5

- 資料搬遷
- 上線測試
- 桌面版退場

## 10. Recommended Build Order

實作順序建議：

1. Supabase project 建立
2. Postgres schema migration
3. Cloudflare Pages 前端骨架
4. Cloudflare Workers API 骨架
5. Supabase Auth 串接
6. 原料主檔 API + UI
7. 產品主檔 API + UI
8. 配方 API + UI
9. 入庫 API + UI
10. 生產 API + UI
11. 庫存中心 API + UI
12. 今日作業 API + UI
13. POS 匯入 API + UI

## 11. Technical Choices

建議組合：

- Frontend: React + Vite + TypeScript
- UI: Tailwind CSS + component primitives
- Form: React Hook Form
- Data fetching: TanStack Query
- API: Cloudflare Workers + Hono
- DB access:
  - 第一版：Supabase client / REST / RPC
  - 第二版若需要更複雜 server query，可再評估 Hyperdrive / direct Postgres access

## 12. Risks

### Risk 1

目前桌面版有不少流程邏輯寫在 UI 事件裡。

處理方式：

- 先把交易規則抽成 Worker API

### Risk 2

SQLite 到 Postgres 雖然不困難，但交易與約束會更嚴格。

處理方式：

- 生產扣料要包 transaction

### Risk 3

桌面版是單機思維，Web 版是多人同時操作。

處理方式：

- 庫存交易全部走後端
- 不讓前端直接改 stock

## 13. Definition Of Done For Web MVP

Web MVP 完成條件：

- 可登入
- 可維護原料與產品
- 可維護產品配方
- 可做原料入庫
- 可做生產並自動扣料
- 可做庫存調整
- 可看低庫存與即期提醒
- 可匯入 POS 銷售

## 14. Next Step

下一步直接開始實作：

1. 建立 `web/` 前端專案
2. 建立 `worker-api/` Cloudflare Worker 專案
3. 建立 `supabase/` migration 結構

本文件完成後，後續工作應改成：

- 先建專案骨架
- 再建 Supabase schema
- 再做第一個模組：Auth + 原料主檔
