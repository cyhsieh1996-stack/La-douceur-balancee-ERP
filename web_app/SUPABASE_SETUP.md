# Supabase Setup

目前已完成：

- 前端 `.env.local` 已填入專案 URL 與 publishable key
- 前端可 build
- Worker API 可 dry-run
- schema migration 檔已準備好

接下來需要在 Supabase Dashboard 做的事：

## 1. 開啟 SQL Editor

進入你的專案：

- [Supabase Project Dashboard](https://supabase.com/dashboard/project/reookovxqozjnefsdczd)

然後打開：

- SQL Editor

## 2. 依序執行這兩個 migration

先執行：

- [20260326_000001_initial_schema.sql](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/supabase/migrations/20260326_000001_initial_schema.sql)

再執行：

- [20260326_000002_triggers_and_rls.sql](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/supabase/migrations/20260326_000002_triggers_and_rls.sql)

## 3. 可選：匯入測試資料

如果你想讓 Web 版原料主檔頁馬上看到資料，可再執行：

- [seed.example.sql](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/web_app/supabase/seed.example.sql)

## 4. 接下來還需要的資訊

之後若要讓 Worker API 寫入 Supabase，需要再提供：

- `service_role key`

位置：

- Project Settings
- Data API / API Keys

## 5. 完成後告訴我

你只要回我：

- `migration 已執行`

如果你也要我直接開始做 Worker 真實寫入，再一起提供：

- `service_role key`
