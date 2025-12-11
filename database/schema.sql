-- ================================
-- SweetERP v1.0 FINAL SCHEMA
-- ================================

PRAGMA foreign_keys = ON;

-- ================================
-- 1) 商品與原料（Items）
-- ================================
DROP TABLE IF EXISTS items;
CREATE TABLE items (
    item_id TEXT PRIMARY KEY,          -- 2+2 編碼：品類代碼 + 口味代碼
    name TEXT NOT NULL,                -- 顯示名稱
    category TEXT,                     -- 類別（FN, MD, CB…）
    unit TEXT NOT NULL,                -- 單位（g, ml, 個…）
    type TEXT NOT NULL,                -- 'raw' 或 'finished'
    track_stock INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    cost REAL,                         -- 最近一次進貨成本
    safety_stock REAL DEFAULT NULL     -- 低庫存警示
);

CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_name ON items(name);


-- ================================
-- 2) 原料與成品庫存異動（Stock Movements）
-- ================================
DROP TABLE IF EXISTS stock_movements;
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    item_id TEXT NOT NULL,
    type TEXT NOT NULL,   -- Purchase / Production_Output / Production_Consume / Sale / Adjust / Waste
    qty_in REAL DEFAULT 0,
    qty_out REAL DEFAULT 0,
    reference_doc TEXT,
    notes TEXT,
    lot_number TEXT,

    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE INDEX idx_sm_item ON stock_movements(item_id);
CREATE INDEX idx_sm_date ON stock_movements(date);


-- ================================
-- 3) 食譜 Recipe Lines（配方）
-- ================================
DROP TABLE IF EXISTS recipes;
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finished_item_id TEXT NOT NULL,
    raw_item_id TEXT NOT NULL,
    qty REAL NOT NULL,
    
    FOREIGN KEY(finished_item_id) REFERENCES items(item_id),
    FOREIGN KEY(raw_item_id) REFERENCES items(item_id)
);

CREATE INDEX idx_recipe_finished ON recipes(finished_item_id);
CREATE INDEX idx_recipe_raw ON recipes(raw_item_id);


-- ================================
-- 4) POS 銷售資料（iCHEF 匯入）
-- ================================

DROP TABLE IF EXISTS sales_header;
CREATE TABLE sales_header (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_sales REAL,
    total_qty REAL,
    source TEXT DEFAULT 'iCHEF'
);

CREATE INDEX idx_sales_header_date ON sales_header(date);


DROP TABLE IF EXISTS sales_detail;
CREATE TABLE sales_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    header_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    item_id TEXT NOT NULL,
    qty REAL NOT NULL,
    unit_price REAL,
    line_amount REAL,

    FOREIGN KEY(header_id) REFERENCES sales_header(id),
    FOREIGN KEY(item_id) REFERENCES items(item_id)
);

CREATE INDEX idx_sales_detail_item ON sales_detail(item_id);
CREATE INDEX idx_sales_detail_header ON sales_detail(header_id);
CREATE INDEX idx_sales_detail_date ON sales_detail(date);


-- ================================
-- 5) 收銀帳（Cash Book）
-- ================================
DROP TABLE IF EXISTS cash_book;
CREATE TABLE cash_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    method TEXT NOT NULL,  -- 現金 / 信用卡 / LinePay 等
    amount REAL NOT NULL,
    type TEXT NOT NULL,    -- In / Out
    notes TEXT
);

CREATE INDEX idx_cashbook_date ON cash_book(date);
