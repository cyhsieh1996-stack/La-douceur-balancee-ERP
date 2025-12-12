import sqlite3
from database.db import get_db

def add_material(name, category, brand, unit, safe_stock):
    """新增原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO raw_materials (name, category, brand, unit, safe_stock, stock)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (name, category, brand, unit, safe_stock))
        conn.commit()
        return True, "新增成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_materials():
    """取得所有原料列表"""
    conn = get_db()
    cursor = conn.cursor()
    # 抓取欄位包含 category
    cursor.execute("SELECT id, name, category, brand, unit, stock, safe_stock FROM raw_materials ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_material(material_id):
    """刪除原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
        conn.commit()
        return True, "刪除成功"
    except Exception as e:
        return False, "無法刪除：此原料可能已被食譜使用中"
    finally:
        conn.close()