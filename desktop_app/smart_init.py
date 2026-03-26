import os
import pandas as pd
import sqlite3
# ⚠️ 修改：多匯入 init_db 來建立表格
from database.db import get_db, init_db

# 設定檔案名稱
FILE_NAME = "item-overview_2025-09-01~2025-09-30.xlsx"

def smart_import():
    print(f"🚀 開始讀取 {FILE_NAME}...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", FILE_NAME)

    if not os.path.exists(file_path):
        print(f"❌ 錯誤：找不到檔案！請確認 {file_path} 是否存在。")
        return

    # 1. 先不設標題讀取，為了尋找標題在哪一行
    try:
        if file_path.endswith('.csv'):
            try:
                df_raw = pd.read_csv(file_path, header=None, encoding='utf-8')
            except:
                df_raw = pd.read_csv(file_path, header=None, encoding='big5')
        else:
            df_raw = pd.read_excel(file_path, header=None)
            
    except Exception as e:
        print(f"❌ 檔案讀取失敗: {e}")
        return

    # 2. 自動尋找標題列
    header_row_index = -1
    target_columns = ['商品名稱', 'Item Name', '名稱', '商品管理', '商品類別']
    
    print("🔍 正在尋找標題列...")
    for i, row in df_raw.head(10).iterrows():
        row_values = [str(v).strip() for v in row.values]
        if any(keyword in row_values for keyword in target_columns):
            header_row_index = i
            print(f"✅ 找到標題了！在第 {i+1} 行")
            break
            
    if header_row_index == -1:
        print("❌ 錯誤：找不到包含 '商品名稱' 或 '商品管理' 的標題列。")
        return

    # 3. 重新讀取
    if file_path.endswith('.csv'):
        try:
            df = pd.read_csv(file_path, header=header_row_index, encoding='utf-8')
        except:
            df = pd.read_csv(file_path, header=header_row_index, encoding='big5')
    else:
        df = pd.read_excel(file_path, header=header_row_index)

    df.columns = [str(c).strip() for c in df.columns]
    print(f"📋 偵測到的欄位: {df.columns.tolist()}")

    # ⚠️ 關鍵修正：在寫入前，先確保資料表存在！
    print("🔨 正在初始化資料庫表格...")
    init_db()

    conn = get_db()
    cursor = conn.cursor()
    
    success_count = 0
    skip_count = 0

    print("🔄 開始寫入資料庫...")

    for index, row in df.iterrows():
        # 抓取名稱
        name = row.get('商品名稱') or row.get('Item Name') or row.get('名稱')
        
        if pd.isna(name) or str(name).strip() == "" or str(name) == "總計":
            continue

        # 抓取類別
        category = (
            row.get('商品管理') or 
            row.get('商品類別') or 
            row.get('Category') or 
            row.get('類別')
        )
        if pd.isna(category) or str(category).strip() == "":
            category = "其他"

        # 計算價格
        try:
            # 處理千分位逗號
            qty_raw = row.get('銷售數量') or row.get('Qty', 0)
            total_raw = row.get('銷售總額') or row.get('Total', 0)
            
            qty_val = str(qty_raw).replace(',', '')
            total_val = str(total_raw).replace(',', '')
            
            qty = float(qty_val)
            total = float(total_val)
            
            if qty > 0:
                price = int(total / qty)
            else:
                price = 0
        except:
            price = 0

        # 檢查重複
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        if cursor.fetchone():
            skip_count += 1
            continue

        cursor.execute("""
            INSERT INTO products (name, category, price, stock)
            VALUES (?, ?, ?, 0)
        """, (name, category, price))
        
        print(f"   ok 新增: {name} (${price})")
        success_count += 1

    conn.commit()
    conn.close()
    
    print("="*30)
    print(f"🎉 匯入完成！")
    print(f"成功新增: {success_count} 筆")
    print(f"重複略過: {skip_count} 筆")
    print("現在請執行 SweetERP_Launcher.command 查看結果")
    print("="*30)

if __name__ == "__main__":
    smart_import()