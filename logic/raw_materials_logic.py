import sqlite3
from database.db import get_db

# ============================================
# 原料管理頁面 (RawMaterialsPage) 會用到的功能
# ============================================

def add_material(name, category, brand, vendor, unit, safe_stock):
    """新增原料 (新增 vendor 參數)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO raw_materials (name, category, brand, vendor, unit, safe_stock, stock)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (name, category, brand, vendor, unit, safe_stock))
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
    # 抓取欄位增加 vendor
    cursor.execute("SELECT id, name, category, brand, vendor, unit, stock, safe_stock FROM raw_materials ORDER BY id DESC")
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

def add_material(name, category, brand, vendor, unit, safe_stock):
    """新增原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO raw_materials (name, category, brand, vendor, unit, safe_stock, stock)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (name, category, brand, vendor, unit, safe_stock))
        conn.commit()
        return True, "新增成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_materials():
    """取得所有原料列表 (管理頁面用)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, brand, vendor, unit, stock, safe_stock FROM raw_materials ORDER BY id DESC")
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

# ============================================
# 入庫/其他頁面 (InboundPage) 會用到的功能
# ============================================

def get_material_dropdown_list():
    """(舊功能) 取得所有原料"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]

# --- 新增以下兩個函式給「兩層式選單」使用 ---

def get_existing_categories():
    """
    取得目前資料庫中已存在的類別 (去除重複)
    回傳: ["粉類", "油脂類", ...]
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM raw_materials WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall()
    conn.close()
    return [row['category'] for row in rows]

def get_materials_by_category(category):
    """
    根據類別篩選原料
    回傳: ["1 - 日本麵粉 (kg)", ...]
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, unit FROM raw_materials WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']} ({row['unit']})" for row in rows]