import sqlite3
from database.db import get_db

def get_all_materials():
    """
    取得所有原料資料
    ⚠️ 排序設定：ORDER BY id ASC (依照 ID 由小到大)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM raw_materials ORDER BY id ASC")
    
    # 將資料轉為字典列表 (List of Dicts)，方便 UI 讀取欄位名稱
    columns = [col[0] for col in cursor.description]
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(columns, row)))
        
    conn.close()
    return result

def search_materials(keyword):
    """
    搜尋原料 (名稱或編號)
    ⚠️ 排序設定：ORDER BY id ASC
    """
    conn = get_db()
    cursor = conn.cursor()
    
    query = f"%{keyword}%"
    sql = """
        SELECT * FROM raw_materials 
        WHERE name_zh LIKE ? OR code LIKE ? OR vendor LIKE ?
        ORDER BY id ASC
    """
    
    cursor.execute(sql, (query, query, query))
    
    columns = [col[0] for col in cursor.description]
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(columns, row)))
        
    conn.close()
    return result

def add_material(data):
    """新增原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 動態產生 INSERT 語法，避免寫死欄位，增加彈性
        keys = list(data.keys())
        values = list(data.values())
        placeholders = ",".join(["?"] * len(keys))
        columns_str = ",".join(keys)
        
        sql = f"INSERT INTO raw_materials ({columns_str}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        return True, "新增成功"
    except Exception as e:
        conn.rollback()
        return False, f"新增失敗: {str(e)}"
    finally:
        conn.close()

def update_material(id, data):
    """更新原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 動態產生 UPDATE 語法
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values())
        values.append(id) # 最後加上 WHERE id = ?
        
        sql = f"UPDATE raw_materials SET {set_clause} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        return True, "更新成功"
    except Exception as e:
        conn.rollback()
        return False, f"更新失敗: {str(e)}"
    finally:
        conn.close()

def delete_material(id):
    """刪除原料"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM raw_materials WHERE id = ?", (id,))
        conn.commit()
        return True, "刪除成功"
    except Exception as e:
        conn.rollback()
        return False, f"刪除失敗: {str(e)}"
    finally:
        conn.close()

def get_material_by_id(id):
    """取得單筆原料詳情 (編輯時會用到)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raw_materials WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
    return None