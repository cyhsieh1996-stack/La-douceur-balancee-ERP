from database.db import get_db

# ============================================================
# 計算某 item 的即時庫存
# ============================================================
def get_stock(item_id):
    conn = get_db()
    cursor = conn.cursor()

    row = cursor.execute("""
        SELECT 
            IFNULL(SUM(qty_in), 0) - IFNULL(SUM(qty_out), 0) AS stock
        FROM stock_movements
        WHERE item_id = ?
    """, (item_id,)).fetchone()

    return row["stock"] if row else 0


# ============================================================
# 取得所有商品（原料 + 成品）與庫存
# ============================================================
def get_all_inventory():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT item_id, name, category, unit, type, safety_stock
        FROM items
        ORDER BY category, name
    """).fetchall()

    result = []

    for r in rows:
        stock = get_stock(r["item_id"])

        result.append({
            "item_id": r["item_id"],
            "name": r["name"],
            "category": r["category"],
            "unit": r["unit"],
            "type": r["type"],
            "safety_stock": r["safety_stock"],
            "stock": stock,
            "low_stock": (r["safety_stock"] is not None and stock < r["safety_stock"])
        })

    return result
