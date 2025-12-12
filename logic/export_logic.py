import pandas as pd
import sqlite3
import os
from datetime import datetime
from database.db import get_db

def export_all_data(target_folder):
    """將所有重要表格匯出成 Excel"""
    try:
        conn = get_db()
        
        # 定義要匯出的表格與工作表名稱
        tables = {
            "products": "產品列表",
            "raw_materials": "原料列表",
            "inbound_records": "入庫紀錄",
            "inventory_adjustments": "庫存調整",
            "production_logs": "生產紀錄",
            "sales_records": "銷售紀錄"
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"SweetERP_Backup_{timestamp}.xlsx"
        filepath = os.path.join(target_folder, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for table_name, sheet_name in tables.items():
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql_query(query, conn)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        conn.close()
        return True, f"匯出成功！\n檔案位置：{filepath}"
        
    except Exception as e:
        return False, f"匯出失敗：{str(e)}"