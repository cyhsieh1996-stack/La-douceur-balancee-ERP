from datetime import datetime, timedelta
from database.db import get_db

def get_workspace_summary():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    first_day = datetime.now().strftime("%Y-%m-01")
    product_target = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    material_target = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    cursor.execute("SELECT COUNT(*) FROM raw_materials WHERE stock < safe_stock AND safe_stock > 0")
    low_stock_count = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM production_logs WHERE expiry_date BETWEEN ? AND ?",
        (today, product_target),
    )
    expiring_products_count = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT COUNT(*) FROM inbound_records WHERE expiry_date BETWEEN ? AND ?",
        (today, material_target),
    )
    expiring_materials_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM inbound_records WHERE date LIKE ?", (f"{today}%",))
    today_inbound_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM production_logs WHERE date LIKE ?", (f"{today}%",))
    today_production_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM sales_records WHERE date LIKE ?", (f"{today}%",))
    today_sales_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM sales_records WHERE date >= ?", (first_day,))
    month_sales_amount = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM raw_materials")
    materials_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0] or 0

    conn.close()
    return {
        "low_stock_count": low_stock_count,
        "expiring_products_count": expiring_products_count,
        "expiring_materials_count": expiring_materials_count,
        "today_inbound_count": today_inbound_count,
        "today_production_count": today_production_count,
        "today_sales_count": today_sales_count,
        "month_sales_amount": month_sales_amount,
        "materials_count": materials_count,
        "products_count": products_count,
    }

def get_low_stock_materials():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT name, stock, safe_stock, unit, vendor FROM raw_materials WHERE stock < safe_stock AND safe_stock > 0 ORDER BY stock ASC")
    rows = cursor.fetchall(); conn.close()
    return rows

def get_expiring_products(days_threshold=7):
    conn = get_db(); cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    target = (datetime.now() + timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    cursor.execute("SELECT p.name, l.batch_number, l.expiry_date, l.qty FROM production_logs l JOIN products p ON l.product_id = p.id WHERE l.expiry_date BETWEEN ? AND ? ORDER BY l.expiry_date ASC", (today, target))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_expiring_raw_materials(days_threshold=30):
    conn = get_db(); cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    target = (datetime.now() + timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    cursor.execute("SELECT m.name, r.batch_number, r.expiry_date, r.qty, m.unit FROM inbound_records r JOIN raw_materials m ON r.material_id = m.id WHERE r.expiry_date BETWEEN ? AND ? ORDER BY r.expiry_date ASC", (today, target))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_top_selling_products(limit=5):
    conn = get_db(); cursor = conn.cursor()
    first_day = datetime.now().strftime("%Y-%m-01")
    cursor.execute("SELECT product_name, SUM(qty) as total_qty FROM sales_records WHERE date >= ? GROUP BY product_name ORDER BY total_qty DESC LIMIT ?", (first_day, limit))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_recent_production(limit=5):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("""
        SELECT l.date, p.name, l.qty, l.batch_number 
        FROM production_logs l 
        JOIN products p ON l.product_id = p.id 
        ORDER BY l.date DESC, l.id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_recent_inbound(limit=5):
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("""
        SELECT r.date, m.name, r.qty, m.unit 
        FROM inbound_records r 
        JOIN raw_materials m ON r.material_id = m.id 
        ORDER BY r.date DESC, r.id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall(); conn.close()
    return rows
