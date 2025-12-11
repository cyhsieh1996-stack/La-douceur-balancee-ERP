# logic/dashboard_logic.py

from database.db import get_connection


# 取得原料總數
def get_total_materials():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM raw_materials;")
    total = c.fetchone()[0]
    conn.close()
    return total


# 取得產品總數（未來會擴充 product table）
def get_total_products():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM products;")
        total = c.fetchone()[0]
    except:
        total = 0
    conn.close()
    return total


# 取得庫存不足的原料（警示）
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

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "name": r[1],
            "current_stock": r[2],
            "safe_stock": r[3],
        })
    return results


# 取得最近 10 筆入庫紀錄
def get_recent_inbound(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT ir.id, rm.name, ir.qty, ir.unit_cost, ir.subtotal, ir.created_at
        FROM inbound_records ir
        JOIN raw_materials rm ON rm.id = ir.material_id
        ORDER BY ir.created_at DESC
        LIMIT ?;
    """, (limit,))
    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "qty": r[2],
            "cost": r[3],
            "subtotal": r[4],
            "time": r[5],
        })
    return result
