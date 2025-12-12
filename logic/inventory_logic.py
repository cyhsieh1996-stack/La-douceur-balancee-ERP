import sqlite3
from database.db import get_db

def get_material_current_stock(material_id):
    """查詢單一原料目前的庫存量"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock, unit FROM raw_materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['stock'], row['unit']
    return 0, ""

def add_inventory_adjustment(material_id, change_qty, action_type, note):
    """
    新增庫存調整紀錄，並更新原料庫存
    change_qty: 正數代表增加，負數代表減少
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. 新增紀錄
        cursor.execute("""
            INSERT INTO inventory_adjustments (material_id, change_qty, action_type, note)
            VALUES (?, ?, ?, ?)
        """, (material_id, change_qty, action_type, note))

        # 2. 更新即時庫存
        cursor.execute("""
            UPDATE raw_materials
            SET stock = stock + ?
            WHERE id = ?
        """, (change_qty, material_id))

        conn.commit()
        return True, "庫存調整成功"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_adjustment_history():
    """取得庫存調整歷史"""
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        SELECT 
            adj.date,
            m.name,
            adj.action_type,
            adj.change_qty,
            m.unit,
            adj.note
        FROM inventory_adjustments adj
        JOIN raw_materials m ON adj.material_id = m.id
        ORDER BY adj.date DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows