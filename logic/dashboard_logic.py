from datetime import datetime, timedelta
from database.db import get_db


# ============================================================
# 本週星期一
# ============================================================
def week_start():
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    return monday


# ============================================================
# 本週銷售 KPI
# ============================================================
def get_week_sales_kpi():
    conn = get_db()
    cursor = conn.cursor()

    monday = week_start()

    rows = cursor.execute("""
        SELECT qty_out, notes
        FROM stock_movements
        WHERE type='Sale'
        AND date >= ?
    """, (str(monday),)).fetchall()

    total_qty = 0
    total_amount = 0

    for r in rows:
        total_qty += r["qty_out"]
        if r["notes"]:
            try:
                amt = float(r["notes"].replace("Imported POS Revenue:", "").strip())
                total_amount += amt
            except:
                pass

    return total_qty, total_amount


# ============================================================
# 本週 Top 3 商品
# ============================================================
def get_top3_products_week():
    conn = get_db()
    cursor = conn.cursor()

    monday = week_start()

    rows = cursor.execute("""
        SELECT item_id, SUM(qty_out) AS total
        FROM stock_movements
        WHERE type='Sale'
        AND date >= ?
        GROUP BY item_id
        ORDER BY total DESC
        LIMIT 3
    """, (str(monday),)).fetchall()

    result = []

    for r in rows:
        item = cursor.execute(
            "SELECT name FROM items WHERE item_id=?", (r["item_id"],)
        ).fetchone()

        result.append({
            "item_id": r["item_id"],
            "name": item["name"] if item else r["item_id"],
            "qty": r["total"]
        })

    return result


# ============================================================
# 低庫存警示
# ============================================================
def get_low_stock_items(limit=5):
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT item_id, name, safety_stock
        FROM items
        WHERE safety_stock IS NOT NULL
    """).fetchall()

    warnings = []
    for r in rows:
        stock_row = cursor.execute("""
            SELECT IFNULL(SUM(qty_in),0) - IFNULL(SUM(qty_out),0)
            FROM stock_movements
            WHERE item_id=?
        """, (r["item_id"],)).fetchone()

        stock = stock_row[0]

        if stock < r["safety_stock"]:
            warnings.append({
                "item_id": r["item_id"],
                "name": r["name"],
                "stock": stock,
                "safety": r["safety_stock"]
            })

    return warnings[:limit]


# ============================================================
# 最新 5 筆生產批號
# ============================================================
def get_recent_lots(limit=5):
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT date, item_id, qty_in, lot_number
        FROM stock_movements
        WHERE type='Production_Output'
        ORDER BY date DESC, id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    result = []
    for r in rows:
        item = cursor.execute("SELECT name FROM items WHERE item_id=?", (r["item_id"],)).fetchone()
        result.append({
            "date": r["date"],
            "item_id": r["item_id"],
            "name": item["name"] if item else r["item_id"],
            "qty": r["qty_in"],
            "lot": r["lot_number"]
        })

    return result
