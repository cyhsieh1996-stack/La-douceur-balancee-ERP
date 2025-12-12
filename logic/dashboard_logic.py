import sqlite3
from datetime import datetime, timedelta
from database.db import get_db

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

def get_top_selling_products(limit=3):
    conn = get_db(); cursor = conn.cursor()
    # 統計本月的熱銷
    first_day = datetime.now().strftime("%Y-%m-01")
    cursor.execute("SELECT product_name, SUM(qty) as total_qty, SUM(amount) as total_rev FROM sales_records WHERE date >= ? GROUP BY product_name ORDER BY total_qty DESC LIMIT ?", (first_day, limit))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_monthly_finance():
    """
    計算 [本月] 與 [上月] 的財務概況
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 計算日期範圍
    now = datetime.now()
    this_month_start = now.strftime("%Y-%m-01")
    
    # 計算上個月的第一天和最後一天
    last_month_end = now.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1).strftime("%Y-%m-%d")
    last_month_end_str = last_month_end.strftime("%Y-%m-%d")

    def query_stats(start_date, end_date=None):
        # 查詢區間內的營業額
        if end_date:
            cursor.execute("SELECT SUM(amount) FROM sales_records WHERE date >= ? AND date <= ?", (start_date, end_date + " 23:59:59"))
        else:
            cursor.execute("SELECT SUM(amount) FROM sales_records WHERE date >= ?", (start_date,))
        revenue = cursor.fetchone()[0] or 0
        
        # 查詢區間內的進貨成本 (qty * unit_price)
        # 注意：這裡假設 inbound_records 有 unit_price 欄位
        if end_date:
            cursor.execute("SELECT SUM(qty * unit_price) FROM inbound_records WHERE date >= ? AND date <= ?", (start_date, end_date + " 23:59:59"))
        else:
            cursor.execute("SELECT SUM(qty * unit_price) FROM inbound_records WHERE date >= ?", (start_date,))
        cost = cursor.fetchone()[0] or 0
        
        return int(revenue), int(cost)

    # 本月數據
    rev_this, cost_this = query_stats(this_month_start)
    profit_this = rev_this - cost_this
    
    # 上月數據
    rev_last, cost_last = query_stats(last_month_start, last_month_end_str)
    profit_last = rev_last - cost_last
    
    conn.close()
    
    return {
        "this_month": {"revenue": rev_this, "cost": cost_this, "profit": profit_this},
        "last_month": {"revenue": rev_last, "cost": cost_last, "profit": profit_last}
    }

def get_dashboard_summary():
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_materials")
    mat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    conn.close()
    return {"material_count": mat_count, "product_count": prod_count}