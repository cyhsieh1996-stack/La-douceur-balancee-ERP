import datetime
from database.db import get_db
from logic.recipes_logic import ensure_recipe_table, get_recipe_usage_preview

def encode_batch_code(date_obj, product_id, seq):
    """
    產生混淆批號
    邏輯：[年碼][月碼][日]-[產品混淆碼]-[流水號]
    範例：2025/12/12, Prod 1, Seq 1 -> AC12-74-01
    """
    base_year = 2025
    year_char = chr(ord('A') + (date_obj.year - base_year))
    
    if date_obj.month < 10:
        month_char = str(date_obj.month)
    else:
        month_map = {10: 'A', 11: 'B', 12: 'C'}
        month_char = month_map.get(date_obj.month, 'X')
        
    day_str = f"{date_obj.day:02d}"
    
    obfuscated_id = hex(product_id * 17 + 99)[2:].upper()
    
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
    
    sql = """
        SELECT COUNT(*) FROM production_logs 
        WHERE product_id = ? AND date LIKE ?
    """
    cursor.execute(sql, (product_id, f"{date_str_db}%"))
    count = cursor.fetchone()[0]
    conn.close()
    
    new_seq = count + 1
    
    return encode_batch_code(today, int(product_id), new_seq)

def add_production_log(product_id, qty, batch_number, expiry_date, note):
    ensure_recipe_table()
    conn = get_db()
    cursor = conn.cursor()
    try:
        qty = float(qty)
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            return False, "找不到產品，請重新整理後再試一次"

        recipe_rows = get_recipe_usage_preview(product_id, qty)
        shortages = [row for row in recipe_rows if float(row["required_qty"]) > float(row["current_stock"])]
        if shortages:
            shortage_lines = [
                f"{row['material_name']} 需要 {row['required_qty']:g}{row['unit']}，現有 {row['current_stock']:g}{row['unit']}"
                for row in shortages
            ]
            return False, "原料不足，無法生產：\n" + "\n".join(shortage_lines)

        cursor.execute("""
            INSERT INTO production_logs (product_id, qty, batch_number, expiry_date, note)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, qty, batch_number, expiry_date, note))

        cursor.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE id = ?
        """, (qty, product_id))

        for row in recipe_rows:
            cursor.execute(
                """
                UPDATE raw_materials
                SET stock = stock - ?
                WHERE id = ?
                """,
                (row["required_qty"], row["material_id"]),
            )

        conn.commit()
        if recipe_rows:
            return True, f"生產登錄成功，已同步扣除 {len(recipe_rows)} 項原料"
        return True, "生產登錄成功，這個產品目前尚未設定配方"
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
