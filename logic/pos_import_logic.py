import pandas as pd
import sqlite3
import datetime
from database.db import get_db

def preview_pos_sales(file_path):
    """
    讀取 POS 報表，並預覽將要扣除的庫存
    回傳: (success, result_list_or_error_msg)
    """
    try:
        # 1. 嘗試讀取 (使用聰明讀取法，自動找標題)
        try:
            if file_path.endswith('.csv'):
                try:
                    df_raw = pd.read_csv(file_path, header=None, encoding='utf-8')
                except:
                    df_raw = pd.read_csv(file_path, header=None, encoding='big5')
            else:
                df_raw = pd.read_excel(file_path, header=None)
        except Exception as e:
            return False, f"檔案讀取失敗: {str(e)}"

        # 尋找標題列
        header_row = -1
        target_cols = ['商品名稱', 'Item Name', '名稱']
        for i, row in df_raw.head(10).iterrows():
            row_str = [str(v).strip() for v in row.values]
            if any(k in row_str for k in target_cols):
                header_row = i
                break
        
        if header_row == -1:
            return False, "找不到對應的標題列 (需包含 '商品名稱' 或 'Item Name')"

        # 重新讀取正確的資料
        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, header=header_row, encoding='utf-8')
            except:
                df = pd.read_csv(file_path, header=header_row, encoding='big5')
        else:
            df = pd.read_excel(file_path, header=header_row)

        df.columns = [str(c).strip() for c in df.columns]

        # 2. 與資料庫比對
        conn = get_db()
        cursor = conn.cursor()
        
        preview_data = []
        
        for index, row in df.iterrows():
            name = row.get('商品名稱') or row.get('Item Name') or row.get('名稱')
            if pd.isna(name) or str(name).strip() == "" or str(name) == "總計":
                continue

            # 抓取銷售數量
            try:
                qty_raw = row.get('銷售數量') or row.get('Qty', 0)
                qty = float(str(qty_raw).replace(',', ''))
            except:
                qty = 0

            if qty <= 0:
                continue

            # 查詢目前庫存
            cursor.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
            db_prod = cursor.fetchone()
            
            if db_prod:
                current_stock = db_prod['stock']
                preview_data.append({
                    "id": db_prod['id'],
                    "name": name,
                    "sales_qty": qty,
                    "current_stock": current_stock,
                    "stock_after": current_stock - qty,
                    "status": "✅ 正常"
                })
            else:
                # 找不到對應產品
                preview_data.append({
                    "id": None,
                    "name": name,
                    "sales_qty": qty,
                    "current_stock": 0,
                    "stock_after": 0,
                    "status": "⚠️ 未建檔 (將略過)"
                })

        conn.close()
        return True, preview_data

    except Exception as e:
        return False, f"處理失敗: {str(e)}"

def confirm_sales_deduction(data_list):
    """
    執行扣庫存
    data_list: 由 preview 產生的列表
    """
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    count = 0
    try:
        for item in data_list:
            if item['id'] is None: # 跳過未建檔
                continue
                
            qty = item['sales_qty']
            prod_id = item['id']
            
            # 1. 扣除庫存
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
            
            # 2. 寫入銷售紀錄 (sales_records)
            cursor.execute("""
                INSERT INTO sales_records (product_name, qty, date, order_id)
                VALUES (?, ?, ?, ?)
            """, (item['name'], qty, today, "POS_IMPORT"))
            
            count += 1
            
        conn.commit()
        return True, f"成功扣除 {count} 項產品庫存！"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()