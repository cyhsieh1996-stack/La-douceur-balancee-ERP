import sqlite3
from database.db import get_db

def add_material(name, category, brand, vendor, unit, unit_price, safe_stock):
    """新增原料 (含單價)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO raw_materials (name, category, brand, vendor, unit, unit_price, safe_stock, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (name, category, brand, vendor, unit, unit_price, safe_stock))
        conn.commit()
        return True, "新增成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_materials():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, brand, vendor, unit, unit_price, stock, safe_stock FROM raw_materials ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_material(material_id):
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

def get_material_dropdown_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]

def get_existing_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM raw_materials WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall()
    conn.close()
    return [row['category'] for row in rows]

def get_materials_by_category(category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]