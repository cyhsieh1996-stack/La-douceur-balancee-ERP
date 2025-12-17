import sqlite3
from database.db import get_db

def add_inventory_adjustment(material_id, qty, action_type, note):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO inventory_adjustments (material_id, action_type, change_qty, note) VALUES (?, ?, ?, ?)", (material_id, action_type, qty, note))
        cursor.execute("UPDATE raw_materials SET stock = stock + ? WHERE id = ?", (qty, material_id))
        conn.commit(); return True, "庫存調整成功"
    except Exception as e: conn.rollback(); return False, str(e)
    finally: conn.close()

def get_adjustment_history():
    conn = get_db(); cursor = conn.cursor()
    # ⚠️ 明確指定順序: 0.date, 1.name, 2.action_type, 3.change_qty, 4.unit, 5.note
    sql = """
        SELECT 
            r.date, m.name, r.action_type, r.change_qty, m.unit, r.note
        FROM inventory_adjustments r
        JOIN raw_materials m ON r.material_id = m.id
        ORDER BY r.date DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall(); conn.close()
    return rows

def get_material_current_stock(mat_id):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT stock, unit FROM raw_materials WHERE id = ?", (mat_id,))
    row = cursor.fetchone(); conn.close()
    if row: return row[0], row[1]
    return 0, ""