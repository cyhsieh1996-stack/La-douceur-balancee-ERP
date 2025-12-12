import sqlite3
from database.db import get_db

def add_inbound_record(material_id, qty, unit_price, batch_number, expiry_date, note):
    """
    新增入庫紀錄，並增加原料庫存
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. 寫入入庫紀錄 (新增 unit_price)
        cursor.execute("""
            INSERT INTO inbound_records (material_id, qty, unit_price, batch_number, expiry_date, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (material_id, qty, unit_price, batch_number, expiry_date, note))

        # 2. 增加原料庫存 (raw_materials table)
        cursor.execute("""
            UPDATE raw_materials
            SET stock = stock + ?
            WHERE id = ?
        """, (qty, material_id))

        conn.commit()
        return True, "入庫成功"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_inbound_history():
    """取得詳細的入庫歷史"""
    conn = get_db()
    cursor = conn.cursor()
    # 新增 unit_price
    sql = """
        SELECT 
            r.date,
            m.name,
            m.brand,
            r.qty,
            m.unit,
            r.unit_price, 
            r.batch_number,
            r.expiry_date,
            r.note
        FROM inbound_records r
        JOIN raw_materials m ON r.material_id = m.id
        ORDER BY r.date DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows