import pandas as pd
import sqlite3
import datetime
from database.db import get_db

def preview_pos_sales(file_path):
    """
    讀取 POS 報表，並預覽將要扣除的庫存 (含強力除錯功能 + 整數優化)
    """
    debug_info = [] 
    
    try:
        # 1. 嘗試讀取檔案
        df_raw = None
        try:
            if file_path.lower().endswith('.csv'):
                try:
                    df_raw = pd.read_csv(file_path, header=None, encoding='utf-8')
                except:
                    try:
                        df_raw = pd.read_csv(file_path, header=None, encoding='big5')
                    except:
                        df_raw = pd.read_csv(file_path, header=None, encoding='utf-8-sig')
            else:
                df_raw = pd.read_excel(file_path, header=None)
        except Exception as e:
            return False, f"檔案讀取失敗: {str(e)}"

        if df_raw is None or df_raw.empty:
            return False, "檔案是空的"

        # 2. 尋找標題列
        header_row_index = -1
        name_keywords = ['商品名稱', 'Item Name', '名稱', '商品', 'Item', 'Product']
        
        for i, row in df_raw.head(20).iterrows():
            row_str = [str(v).strip() for v in row.values]
            if any(k in str(v) for v in row_str for k in name_keywords):
                header_row_index = i
                break
        
        if header_row_index == -1:
            return False, f"找不到標題列。\n系統在前20行找不到包含 {name_keywords} 的列。"

        # 3. 重新讀取正確的資料
        if file_path.lower().endswith('.csv'):
            try:
                df = pd.read_csv(file_path, header=header_row_index, encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(file_path, header=header_row_index, encoding='big5')
                except:
                    df = pd.read_csv(file_path, header=header_row_index, encoding='utf-8-sig')
        else:
            df = pd.read_excel(file_path, header=header_row_index)

        df.columns = [str(c).strip().replace('\n', '') for c in df.columns]
        debug_info.append(f"偵測到的所有欄位: {list(df.columns)}")

        # 4. 辨識欄位
        col_name = None
        col_qty = None

        # 找名稱
        for k in name_keywords:
            for col in df.columns:
                if k in col:
                    col_name = col
                    break
            if col_name: break
        
        # 找數量
        qty_priority = ['銷售量', '銷售數量', 'Qty', '數量', 'Quantity', 'Count', '銷量']
        for k in qty_priority:
            for col in df.columns:
                if k in col and "占比" not in col and "退貨" not in col and "庫存" not in col:
                    col_qty = col
                    break
            if col_qty: break

        if not col_name or not col_qty:
            return False, f"欄位對應失敗。\n名稱欄位: {col_name}\n數量欄位: {col_qty}\n\n所有欄位: {list(df.columns)}"

        # 5. 開始比對
        conn = get_db()
        cursor = conn.cursor()
        preview_data = []
        
        for index, row in df.iterrows():
            name = str(row[col_name]).strip()
            
            if not name or name.lower() in ["nan", "總計", "total", "", "nat"]:
                continue

            try:
                qty_raw = row[col_qty]
                qty_val = str(qty_raw).replace(',', '')
                # ⚠️ 修改：強制轉為整數 int
                qty = int(float(qty_val))
            except:
                qty = 0

            if qty <= 0:
                continue

            cursor.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
            db_prod = cursor.fetchone()
            
            if db_prod:
                # ⚠️ 修改：庫存也強制轉整數顯示
                current_stock = int(db_prod['stock'])
                stock_after = current_stock - qty
                
                # ⚠️ 修改：智慧狀態判斷
                if stock_after < 0:
                    status = "⚠️ 庫存不足 (將變負數)"
                else:
                    status = "✅ 正常"

                preview_data.append({
                    "id": db_prod['id'],
                    "name": name,
                    "sales_qty": qty,
                    "current_stock": current_stock,
                    "stock_after": stock_after,
                    "status": status
                })
            else:
                preview_data.append({
                    "id": None,
                    "name": name,
                    "sales_qty": qty,
                    "current_stock": 0,
                    "stock_after": 0,
                    "status": "❌ 未建檔 (略過)"
                })

        conn.close()
        
        if not preview_data:
            return False, f"檔案讀取成功，但沒有找到有效資料。\n(抓取欄位: 名稱='{col_name}', 數量='{col_qty}')"
            
        return True, preview_data

    except Exception as e:
        return False, f"處理失敗: {str(e)}"

def confirm_sales_deduction(data_list):
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    count = 0
    try:
        for item in data_list:
            if item['id'] is None: 
                continue
            
            # 確保寫入整數
            qty = int(item['sales_qty'])
            prod_id = item['id']
            
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
            cursor.execute("""
                INSERT INTO sales_records (product_name, qty, price, amount, date, order_id)
                VALUES (?, ?, 0, 0, ?, ?)
            """, (item['name'], qty, today, "POS_IMPORT"))
            count += 1
        conn.commit()
        return True, f"成功扣除 {count} 項產品庫存！"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()