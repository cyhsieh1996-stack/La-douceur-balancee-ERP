import sqlite3
from datetime import datetime, timedelta
from database.db import get_db

def get_low_stock_materials():
    """
    取得低於安全庫存的原料
    """
    conn = get_db()
    cursor = conn.cursor()
    # 邏輯：庫存 < 安全庫存 且 安全庫存 > 0 (有些設0代表不管控)
    cursor.execute("""
        SELECT name, stock, safe_stock, unit, vendor
        FROM raw_materials 
        WHERE stock < safe_stock AND safe_stock > 0
        ORDER BY stock ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expiring_batches(days_threshold=7):
    """
    取得即將過期的生產批號 (預設未來 7 天內)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    target_date = (datetime.now() + timedelta(days=days_threshold)).strftime("%Y-%m-%d")
    
    # 搜尋效期在 [今天 ~ 未來N天] 之間的批號
    sql = """
        SELECT 
            p.name, 
            l.batch_number, 
            l.expiry_date,
            l.qty
        FROM production_logs l
        JOIN products p ON l.product_id = p.id
        WHERE l.expiry_date BETWEEN ? AND ?
        ORDER BY l.expiry_date ASC
    """
    cursor.execute(sql, (today, target_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_dashboard_summary():
    """
    取得儀表板上方的統計數字
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. 原料總數
    cursor.execute("SELECT COUNT(*) FROM raw_materials")
    mat_count = cursor.fetchone()[0]
    
    # 2. 產品總數
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    
    # 3. 缺貨原料數
    cursor.execute("SELECT COUNT(*) FROM raw_materials WHERE stock < safe_stock AND safe_stock > 0")
    low_stock_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "material_count": mat_count,
        "product_count": prod_count,
        "low_stock_count": low_stock_count
    }