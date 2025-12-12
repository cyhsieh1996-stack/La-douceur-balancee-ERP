import sqlite3
import datetime
from database.db import get_db

def encode_batch_code(date_obj, product_id, seq):
    """
    產生混淆批號
    邏輯：[年碼][月碼][日]-[產品混淆碼]-[流水號]
    範例：2025/12/12, Prod 1, Seq 1 -> AC12-74-01
    """
    # 1. 年份代碼 (2025=A, 2026=B...)
    base_year = 2025
    year_char = chr(ord('A') + (date_obj.year - base_year))
    
    # 2. 月份代碼 (1-9, 10=A, 11=B, 12=C)
    if date_obj.month < 10:
        month_char = str(date_obj.month)
    else:
        month_map = {10: 'A', 11: 'B', 12: 'C'}
        month_char = month_map.get(date_obj.month, 'X')
        
    # 3. 日期 (01-31)
    day_str = f"{date_obj.day:02d}"
    
    # 4. 產品混淆碼 (線性轉換 + 轉16進位)
    # 算法：(ID * 17 + 99) -> Hex -> 大寫
    # 這樣 ID 1 -> 116 -> 74
    # ID 2 -> 133 -> 85
    obfuscated_id = hex(product_id * 17 + 99)[2:].upper()
    
    # 組合
    return f"{year_char}{month_char}{day_str}-{obfuscated_id}-{seq:02d}"

def generate_batch_number(product_id):
    """
    計算當日該產品的流水號，並產生批號
    """
    if not product_id:
        return ""

    today = datetime.datetime.now()
    date_str_db = today.strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 搜尋今天、這個產品ID 已經有幾筆紀錄了
    sql = """
        SELECT COUNT(*) FROM production_logs 
        WHERE product_id = ? AND date LIKE ?
    """
    cursor.execute(sql, (product_id, f"{date_str_db}%"))
    count = cursor.fetchone()[0]
    conn.close()
    
    new_seq = count + 1
    
    # 使用加密邏輯產生批號
    return encode_batch_code(today, int(product_id), new_seq)

def add_production_log(product_id, qty, batch_number, expiry_date, note):
    """
    新增生產紀錄，並增加產品庫存
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 1. 寫入生產紀錄
        cursor.execute("""
            INSERT INTO production_logs (product_id, qty, batch_number, expiry_date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, qty, batch_number, expiry_date, note))

        # 2. 增加產品庫存 (products table)
        cursor.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE id = ?
        """, (qty, product_id))

        conn.commit()
        return True, "生產登錄成功"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_production_history():
    """取得生產歷史"""
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        SELECT 
            p.date,
            prod.name,
            p.qty,
            p.batch_number,
            p.expiry_date,
            p.note
        FROM production_logs p
        JOIN products prod ON p.product_id = prod.id
        ORDER BY p.date DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows