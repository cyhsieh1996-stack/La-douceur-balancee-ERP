# logic/products_logic.py

from database.db import get_connection


# ------------------------------------------------------
# 新增產品
# ------------------------------------------------------
def add_product(name, category, price):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO products (name, category, price)
        VALUES (?, ?, ?);
    """, (name, category, price))

    conn.commit()
    conn.close()
    return True, "產品已新增"


# ------------------------------------------------------
# 查詢全部產品
# ------------------------------------------------------
def get_all_products():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, category, price, active
        FROM products
        WHERE active = 1
        ORDER BY name ASC;
    """)

    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "price": r[3],
            "active": r[4],
        })
    return result


# ------------------------------------------------------
# 更新產品資訊
# ------------------------------------------------------
def update_product(prod_id, name, category, price):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE products
        SET name=?, category=?, price=?
        WHERE id=?;
    """, (name, category, price, prod_id))

    conn.commit()
    conn.close()
    return True, "產品已更新"


# ------------------------------------------------------
# 刪除產品（停用）
# ------------------------------------------------------
def delete_product(prod_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE products SET active=0 WHERE id=?", (prod_id,))
    conn.commit()
    conn.close()

    return True, "產品已刪除"
