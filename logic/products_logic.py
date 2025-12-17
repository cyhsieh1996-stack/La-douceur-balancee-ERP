import sqlite3
import pandas as pd
from database.db import get_db

def add_product(name, category, price, cost, shelf_life):
    conn = get_db(); cursor = conn.cursor()
    try:
        # 確保有寫入 cost
        cursor.execute("INSERT INTO products (name, category, price, cost, shelf_life, stock) VALUES (?, ?, ?, ?, ?, 0)", (name, category, price, cost, shelf_life))
        conn.commit(); return True, "新增成功"
    except Exception as e: return False, str(e)
    finally: conn.close()

def update_product(product_id, name, category, price, cost, shelf_life):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE products SET name=?, category=?, price=?, cost=?, shelf_life=? WHERE id=?", (name, category, price, cost, shelf_life, product_id))
        conn.commit(); return True, "更新成功"
    except Exception as e: return False, str(e)
    finally: conn.close()

def delete_product(product_id):
    conn = get_db(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit(); return True, "刪除成功"
    except Exception as e: return False, "刪除失敗"
    finally: conn.close()

def get_all_products():
    conn = get_db(); cursor = conn.cursor()
    # ⚠️ 關鍵修改：明確指定欄位順序，對應 UI 的 row[0]~row[6]
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products ORDER BY id ASC")
    rows = cursor.fetchall(); conn.close()
    return rows

def search_products(keyword):
    conn = get_db(); cursor = conn.cursor()
    search_term = f"%{keyword}%"
    # ⚠️ 這裡也要指定順序
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products WHERE name LIKE ? ORDER BY id ASC", (search_term,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_products_by_category(category):
    conn = get_db(); cursor = conn.cursor()
    # ⚠️ 這裡也要指定順序
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_unique_product_categories():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall(); conn.close()
    return [row[0] for row in rows] # 改用 index

def get_product_dropdown_list():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products ORDER BY id ASC")
    rows = cursor.fetchall(); conn.close()
    return [f"{row[0]} - {row[1]}" for row in rows]

def get_product_shelf_life(product_id):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT shelf_life FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone(); conn.close()
    if result and result[0] is not None:
        try: return int(result[0])
        except: return None
    return None

def import_products_from_csv(file_path):
    # (保留原有的匯入邏輯，暫不更動)
    pass