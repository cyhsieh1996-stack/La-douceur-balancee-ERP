import sqlite3
from datetime import datetime, timedelta
from database.db import get_db

def get_low_stock_materials():
    """取得低於安全庫存的原料"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, stock, safe_stock, unit, vendor
        FROM raw_materials 
        WHERE stock < safe_stock AND safe_stock > 0
        ORDER BY stock ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expiring_products(days_threshold=7):
    """即將過期的成品 (批號)"""
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    target_date = (datetime.now() + timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT p.name, l.batch_number, l.expiry_date, l.qty
        FROM production_logs l
        JOIN products p ON l.product_id = p.id
        WHERE l.expiry_date BETWEEN ? AND ?
        ORDER BY l.expiry_date ASC
    """, (today, target_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expiring_raw_materials(days_threshold=30):
    """
    即將過期的原料 (查詢入庫紀錄)
    因為原料通常效期較長，預設抓 30 天內
    """
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    target_date = (datetime.now() + timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT m.name, r.batch_number, r.expiry_date, r.qty, m.unit
        FROM inbound_records r
        JOIN raw_materials m ON r.material_id = m.id
        WHERE r.expiry_date BETWEEN ? AND ?
        ORDER BY r.expiry_date ASC
    """, (today, target_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_top_selling_products(limit=3):
    """
    取得上週熱銷前三名
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 計算 7 天前的日期
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT product_name, SUM(qty) as total_qty, SUM(amount) as total_rev
        FROM sales_records
        WHERE date >= ?
        GROUP BY product_name
        ORDER BY total_qty DESC
        LIMIT ?
    """, (seven_days_ago, limit))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_weekly_finance():
    """
    計算上週財務 (營業額、成本、淨利)
    注意：成本計算依賴 products table 的 'cost' 欄位
    """
    conn = get_db()
    cursor = conn.cursor()
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # 1. 總營業額
    cursor.execute("""
        SELECT SUM(amount) FROM sales_records WHERE date >= ?
    """, (seven_days_ago,))
    revenue = cursor.fetchone()[0] or 0
    
    # 2. 總成本 (銷售數量 * 產品設定的成本)
    # 我們需要 join products 表格來抓 cost
    cursor.execute("""
        SELECT SUM(s.qty * p.cost)
        FROM sales_records s
        JOIN products p ON s.product_name = p.name
        WHERE s.date >= ?
    """, (seven_days_ago,))
    cost = cursor.fetchone()[0] or 0
    
    conn.close()
    
    profit = revenue - cost
    return {
        "revenue": int(revenue),
        "cost": int(cost),
        "profit": int(profit)
    }

def get_dashboard_summary():
    """總數統計"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_materials")
    mat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM raw_materials WHERE stock < safe_stock AND safe_stock > 0")
    low_stock_count = cursor.fetchone()[0]
    conn.close()
    return {
        "material_count": mat_count,
        "product_count": prod_count,
        "low_stock_count": low_stock_count
    }