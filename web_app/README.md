# Web App Workspace

這個資料夾用來放即將上線的 Web 版 ERP。

目前分成三塊：

- [frontend](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/frontend)
  - Cloudflare Pages 前端
- [worker-api](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/worker-api)
  - Cloudflare Workers API
- [supabase](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/supabase)
  - schema migration 與資料庫相關設定

規劃文件：

- [WEB_MIGRATION_PLAN.md](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/WEB_MIGRATION_PLAN.md)
- [NEXT_STEPS.md](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/NEXT_STEPS.md)

目前已落地的骨架：

- `frontend/`
  - React + Vite + TypeScript 結構
  - 已有 Web 首頁與 `materials` 模組骨架
- `worker-api/`
  - Hono + Wrangler 結構
  - 已有 `health`、`dashboard`、`materials` stub API
- `supabase/`
  - 初始 schema migration
  - `updated_at` trigger 與 RLS migration
  - seed example
