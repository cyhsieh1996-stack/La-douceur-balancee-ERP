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

def get_top_selling_products(limit=5):
    conn = get_db(); cursor = conn.cursor()
    first_day = datetime.now().strftime("%Y-%m-01")
    cursor.execute("SELECT product_name, SUM(qty) as total_qty FROM sales_records WHERE date >= ? GROUP BY product_name ORDER BY total_qty DESC LIMIT ?", (first_day, limit))
    rows = cursor.fetchall(); conn.close()
    return rows

# --- 🆕 新增指標 1: 最近生產紀錄 ---
def get_recent_production(limit=5):
    conn = get_db(); cursor = conn.cursor()
    # 抓取最近 5 筆生產紀錄 (日期, 產品名, 數量)
    cursor.execute("""
        SELECT l.date, p.name, l.qty, l.batch_number 
        FROM production_logs l 
        JOIN products p ON l.product_id = p.id 
        ORDER BY l.date DESC, l.id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall(); conn.close()
    return rows

# --- 🆕 新增指標 2: 最近入庫紀錄 ---
def get_recent_inbound(limit=5):
    conn = get_db(); cursor = conn.cursor()
    # 抓取最近 5 筆入庫紀錄 (日期, 原料名, 數量)
    cursor.execute("""
        SELECT r.date, m.name, r.qty, m.unit 
        FROM inbound_records r 
        JOIN raw_materials m ON r.material_id = m.id 
        ORDER BY r.date DESC, r.id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall(); conn.close()
    return rows

def get_monthly_finance():
    conn = get_db(); cursor = conn.cursor()
    now = datetime.now()
    this_month_start = now.strftime("%Y-%m-01")
    last_month_end = now.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1).strftime("%Y-%m-%d")
    last_month_end_str = last_month_end.strftime("%Y-%m-%d")

    def query_stats(start_date, end_date=None):
        if end_date:
            cursor.execute("SELECT SUM(amount) FROM sales_records WHERE date >= ? AND date <= ?", (start_date, end_date + " 23:59:59"))
        else:
            cursor.execute("SELECT SUM(amount) FROM sales_records WHERE date >= ?", (start_date,))
        revenue = cursor.fetchone()[0] or 0
        
        if end_date:
            cursor.execute("SELECT SUM(qty * unit_price) FROM inbound_records WHERE date >= ? AND date <= ?", (start_date, end_date + " 23:59:59"))
        else:
            cursor.execute("SELECT SUM(qty * unit_price) FROM inbound_records WHERE date >= ?", (start_date,))
        cost = cursor.fetchone()[0] or 0
        return int(revenue), int(cost)

    rev_this, cost_this = query_stats(this_month_start)
    profit_this = rev_this - cost_this
    rev_last, cost_last = query_stats(last_month_start, last_month_end_str)
    profit_last = rev_last - cost_last
    conn.close()
    
    return {
        "this_month": {"revenue": rev_this, "cost": cost_this, "profit": profit_this},
        "last_month": {"revenue": rev_last, "cost": cost_last, "profit": profit_last}
    }