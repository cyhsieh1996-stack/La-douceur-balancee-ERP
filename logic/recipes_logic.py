import sqlite3
from database.db import get_db

def get_product_list():
    """取得產品選單 (格式: ID - 名稱)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']}" for row in rows]

def get_current_recipe(product_id):
    """
    讀取某產品目前的配方
    回傳: list of (material_id, material_name, amount, unit)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 這裡做了 JOIN，把原料的名稱和單位一起抓出來顯示
    sql = """
        SELECT 
            r.material_id,
            m.name,
            r.amount,
            m.unit
        FROM recipes r
        JOIN raw_materials m ON r.material_id = m.id
        WHERE r.product_id = ?
    """
    cursor.execute(sql, (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_recipe_to_db(product_id, ingredient_list):
    """
    儲存配方 (採用 全刪除 -> 重寫入 的方式)
    ingredient_list: [(material_id, amount), ...]
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. 先刪除舊的配方
        cursor.execute("DELETE FROM recipes WHERE product_id = ?", (product_id,))
        
        # 2. 逐筆寫入新配方
        for mat_id, amount in ingredient_list:
            cursor.execute("""
                INSERT INTO recipes (product_id, material_id, amount)
                VALUES (?, ?, ?)
            """, (product_id, mat_id, amount))
            
        conn.commit()
        return True, "配方儲存成功！"
    except Exception as e:
        conn.rollback()
        return False, f"儲存失敗: {str(e)}"
    finally:
        conn.close()