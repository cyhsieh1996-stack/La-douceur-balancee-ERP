import sqlite3
from datetime import datetime
from database.db import get_db

def ensure_inbound_table():
    """確保 inbound_records 資料表存在，避免查詢錯誤"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER,
            qty REAL,
            unit_price REAL,
            batch_number TEXT,
            expiry_date TEXT,
            note TEXT,
            date TEXT,
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        )
    """)
    conn.commit()
    conn.close()

def add_inbound_record(material_id, qty, price, batch_number, expiry_date, note):
    """新增入庫紀錄，並自動增加原料庫存"""
    ensure_inbound_table() # 確保表格存在
    conn = get_db()
    cursor = conn.cursor()
    try:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 轉型檢查
        qty = float(qty)
        price = float(price) if price else 0.0
        
        # 1. 新增入庫紀錄
        cursor.execute("""
            INSERT INTO inbound_records (material_id, qty, unit_price, batch_number, expiry_date, note, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (material_id, qty, price, batch_number, expiry_date, note, date_str))

        # 2. 更新原料庫存 (Stock + Qty)；若有單價則同步更新參考單價
        if price > 0:
            cursor.execute("""
                UPDATE raw_materials
                SET stock = stock + ?, unit_price = ?
                WHERE id = ?
            """, (qty, price, material_id))
        else:
            cursor.execute("""
                UPDATE raw_materials
                SET stock = stock + ?
                WHERE id = ?
            """, (qty, material_id))

        conn.commit()
        return True, "入庫成功！庫存已更新。"
    except Exception as e:
        conn.rollback()
        return False, f"入庫失敗: {str(e)}"
    finally:
        conn.close()

def get_recent_inbound_records(limit=20):
    """取得最近的入庫紀錄"""
    ensure_inbound_table() # 確保表格存在
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 關聯 raw_materials 取得名稱與單位
        cursor.execute("""
            SELECT r.date, m.name, r.qty, m.unit, r.batch_number, r.expiry_date
            FROM inbound_records r
            JOIN raw_materials m ON r.material_id = m.id
            ORDER BY r.date DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"查詢入庫紀錄失敗: {e}")
        return []
    finally:
        conn.close()
