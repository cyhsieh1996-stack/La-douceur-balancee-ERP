# dashboard_logic.py
from database.db import get_db


# ======================================
# 原料庫存總量
# ======================================
def get_total_material_stock():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT SUM(stock) FROM raw_materials;")
    result = cur.fetchone()[0]

    return result if result else 0


# ======================================
# 產品庫存總量
# ======================================
def get_total_product_stock():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT SUM(stock) FROM products;")
    result = cur.fetchone()[0]

    return result if result else 0


# ======================================
# 低庫存原料（預警）
# ======================================
def get_low_stock_materials(threshold=50):
    """
    threshold：低於多少就列入警示（可之後做設定）
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, stock, unit 
        FROM raw_materials
        WHERE stock < ?
        ORDER BY stock ASC;
    """, (threshold,))

    rows = cur.fetchall()

    return [
        {"name": r[0], "stock": r[1], "unit": r[2]}
        for r in rows
    ]
