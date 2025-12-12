# database/db.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sweet_erp.db")


# ------------------------------------------------------
# 建立資料表
# ------------------------------------------------------
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ---------------------
    # 原料
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            spec TEXT,
            unit TEXT NOT NULL DEFAULT 'g',
            safe_stock REAL NOT NULL DEFAULT 0,
            current_stock REAL NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
    """)

    # ---------------------
    # 入庫紀錄
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS inbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            qty REAL NOT NULL,
            unit_cost REAL NOT NULL,
            subtotal REAL NOT NULL,
            supplier TEXT,
            note TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        );
    """)

    # ---------------------
    # 產品資料
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
    """)

    # ---------------------
    # 食譜（產品配方）
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipe_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        );
    """)

    # ---------------------
    # 生產紀錄
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS production_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            batch INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
    """)

    # ---------------------
    # POS 銷售資料
    # ---------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS pos_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            subtotal REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------
# 取得資料庫連線
# ------------------------------------------------------
def get_connection():
    initialize_database()
    return sqlite3.connect(DB_PATH)
