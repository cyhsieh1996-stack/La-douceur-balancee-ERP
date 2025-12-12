# logic/pos_logic.py

import csv
from database.db import get_connection


# ------------------------------------------------------
# 匯入 POS 銷售 CSV
# 格式必須包含：日期, 商品名稱, 數量, 單價, 小計
# ------------------------------------------------------
def import_pos_csv(file_path):
    conn = get_connection()
    c = conn.cursor()

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("日期")
            name = row.get("商品名稱")
            qty = int(row.get("數量"))
            price = float(row.get("單價"))
            subtotal = float(row.get("小計"))

            c.execute("""
                INSERT INTO pos_sales (date, product_name, qty, price, subtotal)
                VALUES (?, ?, ?, ?, ?);
            """, (date, name, qty, price, subtotal))

    conn.commit()
    conn.close()
    return True, "POS資料已匯入完成"


# ------------------------------------------------------
# KPI：本週銷售總額
# ------------------------------------------------------
def get_week_sales_kpi():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT SUM(subtotal)
        FROM pos_sales
        WHERE date >= date('now', '-6 days');
    """)

    val = c.fetchone()[0] or 0
    conn.close()
    return val
