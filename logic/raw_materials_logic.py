import sqlite3
from database.db import get_db

def add_material(name, category, brand, vendor, unit, safe_stock):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO raw_materials (name, category, brand, vendor, unit, unit_price, safe_stock, stock) VALUES (?, ?, ?, ?, ?, 0, ?, 0)", (name, category, brand, vendor, unit, safe_stock))
        conn.commit(); return True, "新增成功"
    except Exception as e: return False, str(e)
    finally: conn.close()

def update_material(mat_id, name, category, brand, vendor, unit, safe_stock):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE raw_materials SET name=?, category=?, brand=?, vendor=?, unit=?, safe_stock=? WHERE id=?", (name, category, brand, vendor, unit, safe_stock, mat_id))
        conn.commit(); return True, "更新成功"
    except Exception as e: return False, str(e)
    finally: conn.close()

def delete_material(material_id):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
        conn.commit(); return True, "刪除成功"
    except Exception as e: return False, "無法刪除：此原料可能已被紀錄使用中"
    finally: conn.close()

def get_all_materials():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, brand, vendor, unit, unit_price, stock, safe_stock FROM raw_materials ORDER BY id DESC")
    rows = cursor.fetchall(); conn.close()
    return rows

# ⚠️ 新增搜尋功能
def search_materials(keyword):
    conn = get_db(); cursor = conn.cursor()
    search_term = f"%{keyword}%"
    sql = """
        SELECT id, name, category, brand, vendor, unit, unit_price, stock, safe_stock 
        FROM raw_materials 
        WHERE name LIKE ? OR brand LIKE ? OR vendor LIKE ?
        ORDER BY id DESC
    """
    cursor.execute(sql, (search_term, search_term, search_term))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_material_dropdown_list():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials ORDER BY id ASC")
    rows = cursor.fetchall(); conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]

def get_existing_categories():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM raw_materials WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall(); conn.close()
    return [row['category'] for row in rows]

def get_all_vendors():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT vendor FROM raw_materials WHERE vendor IS NOT NULL AND vendor != ''")
    rows = cursor.fetchall(); conn.close()
    return [row['vendor'] for row in rows]

def get_materials_by_category(category):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall(); conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]