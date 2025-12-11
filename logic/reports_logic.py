from database.db import get_connection


# ---------------------------------------------------
# 1. 庫存現況報表
# ---------------------------------------------------
def get_inventory_report():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT i.item_id, i.name, i.unit,
               IFNULL(SUM(sm.qty_in - sm.qty_out), 0) AS stock
        FROM items i
        LEFT JOIN stock_movements sm ON sm.item_id = i.item_id
        GROUP BY i.item_id
        ORDER BY i.item_id
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------
# 2. 成品成本報表
# ---------------------------------------------------
def get_cost_report():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT rp.finished_item_id AS item_id,
               items.name,
               SUM(rp.qty * it.cost) AS recipe_cost
        FROM recipes rp
        JOIN items ON items.item_id = rp.finished_item_id
        JOIN items it ON it.item_id = rp.raw_item_id
        GROUP BY rp.finished_item_id
        ORDER BY recipe_cost ASC
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------
# 3. 銷售排行
# ---------------------------------------------------
def get_sales_ranking():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT sd.item_id, it.name,
               SUM(sd.qty) AS total_qty,
               SUM(sd.line_amount) AS revenue
        FROM sales_detail sd
        JOIN items it ON it.item_id = sd.item_id
        GROUP BY sd.item_id
        ORDER BY revenue DESC
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------
# 4. 毛利報表（Revenue - Recipe Cost）
# ---------------------------------------------------
def get_gross_margin_report():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT 
            sd.item_id,
            it.name,
            SUM(sd.line_amount) AS revenue,
            (SELECT SUM(r.qty * raw.cost)
             FROM recipes r
             JOIN items raw ON raw.item_id = r.raw_item_id
             WHERE r.finished_item_id = sd.item_id
            ) AS cost,
            SUM(sd.line_amount) - 
            (SELECT SUM(r.qty * raw.cost)
             FROM recipes r
             JOIN items raw ON raw.item_id = r.raw_item_id
             WHERE r.finished_item_id = sd.item_id
            ) AS margin
        FROM sales_detail sd
        JOIN items it ON it.item_id = sd.item_id
        GROUP BY sd.item_id
        ORDER BY margin DESC
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------
# 5. 支付方式報表
# ---------------------------------------------------
def get_payment_report():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT method, 
               SUM(amount) AS total_amount,
               COUNT(*) AS count
        FROM cashbook
        GROUP BY method
        ORDER BY total_amount DESC
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]
