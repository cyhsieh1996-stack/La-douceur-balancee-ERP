# Deprecated Files

這個資料夾與專案內部分舊檔案用來保留歷史版本參考，不是目前正式執行路徑。

目前正式使用的資料模型是：

- `raw_materials`
- `products`
- `inbound_records`
- `production_logs`
- `sales_records`
- `inventory_adjustments`

如果看到 `items`、`stock_movements`、`recipes`、`sales_detail`、`cash_book` 等舊表名，
請先確認那是歷史檔案，不要直接當成主系統 schema 使用。
