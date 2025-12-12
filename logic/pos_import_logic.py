import pandas as pd
import sqlite3
import datetime
from database.db import get_db

def preview_pos_sales(file_path):
    # ... (上半部預覽邏輯保持不變，為了節省空間，請保留您原本成功的預覽代碼) ...
    # ... (如果您需要完整版請告訴我，但重點是下面的 confirm_sales_deduction) ...
    
    # 這裡直接貼上完整的 preview_pos_sales 以防萬一
    debug_info = [] 
    try:
        df_raw = None
        try:
            if file_path.lower().endswith('.csv'):
                try: df_raw = pd.read_csv(file_path, header=None, encoding='utf-8')
                except: 
                    try: df_raw = pd.read_csv(file_path, header=None, encoding='big5')
                    except: df_raw = pd.read_csv(file_path, header=None, encoding='utf-8-sig')
            else: df_raw = pd.read_excel(file_path, header=None)
        except Exception as e: return False, f"檔案讀取失敗: {str(e)}"

        if df_raw is None or df_raw.empty: return False, "檔案是空的"

        header_row_index = -1
        name_keywords = ['商品名稱', 'Item Name', '名稱', '商品', 'Item', 'Product']
        for i, row in df_raw.head(20).iterrows():
            row_str = [str(v).strip() for v in row.values]
            if any(k in str(v) for v in row_str for k in name_keywords):
                header_row_index = i; break
        
        if header_row_index == -1: return False, f"找不到標題列"

        if file_path.lower().endswith('.csv'):
            try: df = pd.read_csv(file_path, header=header_row_index, encoding='utf-8')
            except: 
                try: df = pd.read_csv(file_path, header=header_row_index, encoding='big5')
                except: df = pd.read_csv(file_path, header=header_row_index, encoding='utf-8-sig')
        else: df = pd.read_excel(file_path, header=header_row_index)

        df.columns = [str(c).strip().replace('\n', '') for c in df.columns]
        
        col_name = None; col_qty = None
        for k in name_keywords:
            for col in df.columns:
                if k in col: col_name = col; break
            if col_name: break
        
        qty_priority = ['銷售量', '銷售數量', 'Qty', '數量', 'Quantity', 'Count', '銷量']
        for k in qty_priority:
            for col in df.columns:
                if k in col and "占比" not in col and "退貨" not in col and "庫存" not in col: col_qty = col; break
            if col_qty: break

        if not col_name or not col_qty: return False, f"欄位對應失敗"

        conn = get_db(); cursor = conn.cursor(); preview_data = []
        for index, row in df.iterrows():
            name = str(row[col_name]).strip()
            if not name or name.lower() in ["nan", "總計", "total", "", "nat"]: continue
            try: qty = int(float(str(row[col_qty]).replace(',', '')))
            except: qty = 0
            if qty <= 0: continue

            cursor.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
            db_prod = cursor.fetchone()
            
            if db_prod:
                current_stock = int(db_prod['stock'])
                stock_after = current_stock - qty
                status = "⚠️ 庫存不足 (將變負數)" if stock_after < 0 else "✅ 正常"
                preview_data.append({"id": db_prod['id'], "name": name, "sales_qty": qty, "current_stock": current_stock, "stock_after": stock_after, "status": status})
            else:
                preview_data.append({"id": None, "name": name, "sales_qty": qty, "current_stock": 0, "stock_after": 0, "status": "❌ 未建檔"})

        conn.close()
        if not preview_data: return False, "沒讀到有效資料"
        return True, preview_data
    except Exception as e: return False, str(e)

# ⚠️ 重點修改在這裡：一定要覆蓋這個函式
def confirm_sales_deduction(data_list):
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    count = 0
    try:
        for item in data_list:
            if item['id'] is None: continue
            
            qty = int(item['sales_qty'])
            prod_id = item['id']
            
            # 1. 關鍵：去查這個產品現在賣多少錢
            cursor.execute("SELECT price FROM products WHERE id = ?", (prod_id,))
            row = cursor.fetchone()
            # 如果沒設售價，就預設 0
            price = row['price'] if row and row['price'] else 0
            
            # 2. 計算總金額
            amount = price * qty

            # 3. 扣庫存
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
            
            # 4. 寫入銷售紀錄 (包含金額)
            cursor.execute("""
                INSERT INTO sales_records (product_name, qty, price, amount, date, order_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item['name'], qty, price, amount, today, "POS_IMPORT"))
            
            count += 1
            
        conn.commit()
        return True, f"成功扣除 {count} 項產品庫存！"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()