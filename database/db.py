import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sweet_erp.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 1. 原料表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            brand TEXT,
            vendor TEXT,
            unit TEXT,
            unit_price REAL DEFAULT 0,
            stock REAL DEFAULT 0,
            safe_stock REAL DEFAULT 0
        );
    """)

    # 2. 產品表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            cost REAL DEFAULT 0,
            stock REAL DEFAULT 0,
            shelf_life INTEGER
        );
    """)

    # --- (原第3點 食譜表 已移除) ---

    # 4. 入庫紀錄 (修改：新增 unit_price)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            qty REAL NOT NULL,
            unit_price REAL DEFAULT 0,  -- 新增這一行
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            batch_number TEXT,
            expiry_date TEXT,
            note TEXT,
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        );
    """)

    # 5. 生產紀錄
    cur.execute("""
        CREATE TABLE IF NOT EXISTS production_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            qty REAL NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            batch_number TEXT,
            expiry_date TEXT,
            note TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
    """)

    # 6. 銷售紀錄
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            qty REAL,
            price REAL,
            amount REAL,
            date TEXT,
            order_id TEXT
        );
    """)

    # 7. 庫存調整紀錄
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            change_qty REAL NOT NULL,
            action_type TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        );
    """)

    conn.commit()
    conn.close()
    print("資料庫初始化完成")

if __name__ == "__main__":
    init_db()