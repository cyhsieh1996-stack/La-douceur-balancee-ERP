import pandas as pd
import sqlite3
import os
from datetime import datetime
from database.db import get_db

def process_pos_file(file_path):
    """
    讀取 POS 銷售報表 (Excel/CSV) 並寫入資料庫
    假設欄位有：[日期], [品名], [數量], [單價], [總金額], [單號]
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. 讀取檔案
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 2. 簡單的欄位對應 (這裡做一個防呆，假設使用者欄位可能不同)
        # 我們嘗試尋找關鍵字，如果找不到就報錯
        cols = df.columns.tolist()
        
        # 簡易對應邏輯 (您可以根據實際 POS 報表調整)
        col_map = {}
        for c in cols:
            if "品名" in c or "商品" in c or "Product" in c: col_map["name"] = c
            elif "數量" in c or "Qty" in c: col_map["qty"] = c
            elif "金額" in c or "Amount" in c or "Total" in c: col_map["amount"] = c
            elif "單價" in c or "Price" in c: col_map["price"] = c
            elif "日期" in c or "Date" in c: col_map["date"] = c
            elif "單號" in c or "ID" in c: col_map["order_id"] = c

        # 檢查必要欄位
        if "name" not in col_map or "qty" not in col_map or "amount" not in col_map:
            return False, "無法識別欄位！請確保 Excel 包含：品名、數量、金額"

        count = 0
        for _, row in df.iterrows():
            name = str(row[col_map["name"]])
            qty = float(row[col_map["qty"]])
            amount = float(row[col_map["amount"]])
            
            price = float(row[col_map["price"]]) if "price" in col_map else (amount/qty if qty!=0 else 0)
            date = str(row[col_map["date"]]) if "date" in col_map else datetime.now().strftime("%Y-%m-%d")
            order_id = str(row[col_map["order_id"]]) if "order_id" in col_map else f"POS-{datetime.now().strftime('%Y%m%d')}"

            cursor.execute("""
                INSERT INTO sales_records (product_name, qty, price, amount, date, order_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, qty, price, amount, date, order_id))
            count += 1

        conn.commit()
        return True, f"成功匯入 {count} 筆銷售資料！"

    except Exception as e:
        conn.rollback()
        return False, f"匯入失敗: {str(e)}"
    finally:
        conn.close()

def get_sales_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, order_id, product_name, qty, price, amount FROM sales_records ORDER BY date DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    return rows