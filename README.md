# La-douceur-balancee-ERP

甜點門市/工作室用的桌面 ERP，使用 `customtkinter` 與 SQLite。

## 目前正式使用的資料模型

主程式目前以這幾張表為準：

- `raw_materials`
- `products`
- `inbound_records`
- `production_logs`
- `sales_records`
- `inventory_adjustments`

舊的 `items` / `stock_movements` / `recipes` 架構仍有部分歷史檔案殘留，但已不是目前 GUI 主流程使用的模型。

## 主要入口

- 啟動桌面程式：[main.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/main.py)
- 資料庫初始化：[database/db.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/database/db.py)
- 原料管理頁：[ui/pages/raw_materials_page.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/ui/pages/raw_materials_page.py)
- 入庫頁：[ui/pages/inbound_page.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/ui/pages/inbound_page.py)
- 生產頁：[ui/pages/production_page.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/ui/pages/production_page.py)
- 庫存調整頁：[ui/pages/inventory_page.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/ui/pages/inventory_page.py)
- 戰情中心：[ui/pages/dashboard_page.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/ui/pages/dashboard_page.py)

## 啟動方式

1. 確認安裝 Python 3 與相依套件。
2. 執行：

```bash
python3 main.py
```

首次啟動會自動初始化資料庫，並在專案根目錄的 `backups/` 建立備份。

## 匯入腳本

- [smart_init.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/smart_init.py)
  - 從報表匯入 `products`
- [import_products_from_excel.py](/Users/CYHsieh/Desktop/La-douceur-balancee-ERP/import_products_from_excel.py)
  - 從 Excel 匯入甜點產品到現行 `products` 表

## 備註

- 專案內有 `env/` 與 `venv/`，但是否實際使用需依本機環境確認。
- 根目錄的 `sweet_erp.db` 是目前主程式使用的 SQLite 檔案。
