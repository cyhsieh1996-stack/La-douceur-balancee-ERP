import sqlite3
import os

# SweetERP 資料庫位置
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "sweet_erp.db")

def get_db():
    """取得 SQLite 資料庫連線（每次呼叫回傳新連線）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 讓 cursor.fetchall() 回傳 dict-like 物件
    return conn
