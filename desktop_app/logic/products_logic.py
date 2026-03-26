from database.db import get_db

def add_product(name, category, price, cost, shelf_life):
    conn = get_db(); cursor = conn.cursor()
    try:
        name = (name or "").strip()
        if not name:
            return False, "名稱不可空白"
        cursor.execute("SELECT id FROM products WHERE LOWER(name)=LOWER(?)", (name,))
        if cursor.fetchone():
            return False, "已有同名產品"
        cursor.execute("INSERT INTO products (name, category, price, cost, shelf_life, stock) VALUES (?, ?, ?, ?, ?, 0)", (name, category, price, cost, shelf_life))
        conn.commit(); return True, "新增成功"
    except Exception as e: return False, str(e)
    finally: conn.close()

def update_product(product_id, name, category, price, cost, shelf_life):
    conn = get_db(); cursor = conn.cursor()
    try:
        name = (name or "").strip()
        if not name:
            return False, "名稱不可空白"
        cursor.execute("SELECT id FROM products WHERE LOWER(name)=LOWER(?) AND id != ?", (name, product_id))
        if cursor.fetchone():
            return False, "已有同名產品"
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
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products ORDER BY id ASC")
    rows = cursor.fetchall(); conn.close()
    return rows

def search_products(keyword):
    conn = get_db(); cursor = conn.cursor()
    search_term = f"%{keyword}%"
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products WHERE name LIKE ? ORDER BY id ASC", (search_term,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_products_by_category(category):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, cost, shelf_life, stock FROM products WHERE category = ? ORDER BY id ASC", (category,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_unique_product_categories():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall(); conn.close()
    return [row[0] for row in rows]

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
    raise NotImplementedError("請使用 import_products_from_excel.py 或 UI 的批次貼上匯入流程")
