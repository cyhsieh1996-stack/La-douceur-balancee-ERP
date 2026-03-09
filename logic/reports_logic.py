from database.db import get_db

def _fetch_dicts(query, params=()):
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def _table_exists(table_name):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,)
    ).fetchone()
    conn.close()
    return bool(row)

# ---------------------------------------------------
# 1. 庫存現況報表
# ---------------------------------------------------
def get_inventory_report():
    rows = _fetch_dicts(
        """
        SELECT 'raw_material' AS type, id, name, unit, stock
        FROM raw_materials
        UNION ALL
        SELECT 'product' AS type, id, name, '' AS unit, stock
        FROM products
        ORDER BY type, id
        """
    )
    return rows


# ---------------------------------------------------
# 2. 成品成本報表
# ---------------------------------------------------
def get_cost_report():
    rows = _fetch_dicts(
        """
        SELECT id, name, category, price, cost, stock
        FROM products
        ORDER BY category, name
        """
    )
    return rows


# ---------------------------------------------------
# 3. 銷售排行
# ---------------------------------------------------
def get_sales_ranking():
    rows = _fetch_dicts(
        """
        SELECT product_name,
               SUM(qty) AS total_qty,
               SUM(amount) AS revenue
        FROM sales_records
        GROUP BY product_name
        ORDER BY revenue DESC
        """
    )
    return rows


# ---------------------------------------------------
# 4. 毛利報表（Revenue - Recipe Cost）
# ---------------------------------------------------
def get_gross_margin_report():
    rows = _fetch_dicts(
        """
        SELECT
            s.product_name,
            SUM(s.amount) AS revenue,
            SUM(s.qty * COALESCE(p.cost, 0)) AS cost,
            SUM(s.amount) - SUM(s.qty * COALESCE(p.cost, 0)) AS margin
        FROM sales_records s
        LEFT JOIN products p ON p.name = s.product_name
        GROUP BY s.product_name
        ORDER BY margin DESC
        """
    )
    return rows


# ---------------------------------------------------
# 5. 支付方式報表
# ---------------------------------------------------
def get_payment_report():
    if not _table_exists("cash_book"):
        return []

    rows = _fetch_dicts(
        """
        SELECT method,
               SUM(amount) AS total_amount,
               COUNT(*) AS count
        FROM cash_book
        GROUP BY method
        ORDER BY total_amount DESC
        """
    )
    return rows
