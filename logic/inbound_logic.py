import sqlite3
from database.db import get_db

def add_inbound_record(material_id, qty, batch_number, expiry_date, note):
    """
    新增入庫紀錄 (含批號與效期)，並同時增加原料庫存
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. 新增入庫紀錄
        cursor.execute("""
            INSERT INTO inbound_records (material_id, qty, batch_number, expiry_date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (material_id, qty, batch_number, expiry_date, note))

        # 2. 同步更新原料庫存 (庫存 = 原本庫存 + 入庫量)
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
    """
    取得入庫歷史紀錄 (包含批號、效期)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    sql = """
    SELECT 
        r.id,
        r.date,
        m.name,
        m.brand,
        r.qty,
        m.unit,
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