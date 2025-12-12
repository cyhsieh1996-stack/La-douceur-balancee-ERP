import sqlite3
import pandas as pd
from database.db import get_db

def add_product(name, category, price, cost, shelf_life):
    """新增產品 (含成本)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (name, category, price, cost, shelf_life, stock)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (name, category, price, cost, shelf_life))
        conn.commit()
        return True, "新增成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_product(product_id, name, category, price, cost, shelf_life):
    """更新產品 (含成本)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE products 
            SET name = ?, category = ?, price = ?, cost = ?, shelf_life = ?
            WHERE id = ?
        """, (name, category, price, cost, shelf_life, product_id))
        conn.commit()
        return True, "更新成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_unique_product_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall()
    conn.close()
    return [row['category'] for row in rows]

def get_products_by_category(category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return True, "刪除成功"
    except Exception as e:
        return False, "刪除失敗"
    finally:
        conn.close()

def get_product_dropdown_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [f"{row['id']} - {row['name']}" for row in rows]

def get_product_shelf_life(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT shelf_life FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] is not None:
        try:
            return int(result[0])
        except:
            return None
    return None

# ==========================================
# 從 POS CSV 匯入產品
# ==========================================
def import_products_from_csv(file_path):
    conn = get_db()
    cursor = conn.cursor()
    count_success = 0
    count_skip = 0
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='big5')

        df.columns = [str(c).strip() for c in df.columns]
        
        for index, row in df.iterrows():
            name = row.get('商品名稱') or row.get('Item Name') or row.get('名稱')
            if not name or pd.isna(name): continue

            category = row.get('商品管理') or row.get('商品類別') or row.get('Category') or row.get('類別')
            if not category or pd.isna(category): category = "其他"

            try:
                qty = float(str(row.get('銷售數量', 0)).replace(',',''))
                total = float(str(row.get('銷售總額', 0)).replace(',',''))
                price = int(total / qty) if qty > 0 else 0
            except:
                price = 0

            cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
            if cursor.fetchone():
                count_skip += 1
                continue

            # 匯入時，cost 預設 0
            cursor.execute("""
                INSERT INTO products (name, category, price, cost, shelf_life, stock)
                VALUES (?, ?, ?, 0, NULL, 0)
            """, (name, category, price))
            count_success += 1

        conn.commit()
        return True, f"匯入完成！\n成功: {count_success}\n略過: {count_skip}"
    except Exception as e:
        return False, f"匯入失敗: {str(e)}"
    finally:
        conn.close()