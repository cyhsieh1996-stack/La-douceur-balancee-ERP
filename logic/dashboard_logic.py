# logic/dashboard_logic.py

from database.db import get_connection
from logic.pos_logic import get_week_sales_kpi


# ------------------------------------------------------
# 原料數量
# ------------------------------------------------------
def get_total_materials():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM raw_materials WHERE active=1;")
    total = c.fetchone()[0]
    conn.close()
    return total


# ------------------------------------------------------
# 產品數量
# ------------------------------------------------------
def get_total_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products WHERE active=1;")
    total = c.fetchone()[0]
    conn.close()
    return total


# ------------------------------------------------------
# 庫存不足清單
# ------------------------------------------------------
def get_low_stock_materials():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, current_stock, safe_stock
        FROM raw_materials
        WHERE current_stock < safe_stock AND active = 1;
    """)
    rows = c.fetchall()
    conn.close()

    return [{
        "id": r[0],
        "name": r[1],
        "current_stock": r[2],
        "safe_stock": r[3],
    } for r in rows]


# ------------------------------------------------------
# 本週 POS 銷售
# ------------------------------------------------------
def get_weekly_sales():
    return get_week_sales_kpi()
