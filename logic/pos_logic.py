import pandas as pd
from datetime import datetime, timedelta
from database.db import get_db
from .items_logic import get_item_by_name


# ============================================================
# 取得上一週日期範圍 (週一 ～ 週日）
# ============================================================
def get_last_week_range():
    today = datetime.now().date()
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday, last_sunday


# ============================================================
# 匯入 POS 銷售報表：Item-Overview / Sales-Ranking
# ============================================================
def import_pos_item_overview(file_path):
    df = pd.read_excel(file_path)

    conn = get_db()
    cursor = conn.cursor()

    last_mon, last_sun = get_last_week_range()

    missing_products = []
    imported_count = 0

    for _, row in df.iterrows():
        name = str(row.get("Name")).strip()
        qty = row.get("QtySold", 0)
        amount = row.get("Revenue", 0)

        # 跳過空行或非甜點商品
        if not name or qty == 0:
            continue

        # ERP 尋找對應商品
        item = get_item_by_name(name)

        if not item:
            missing_products.append(name)
            continue

        item_id = item["item_id"]

        # 建立 Sale movement
        cursor.execute("""
            INSERT INTO stock_movements (date, item_id, type, qty_in, qty_out, notes)
            VALUES (?, ?, 'Sale', 0, ?, ?)
        """, (str(last_sun), item_id, qty, f"Imported POS Revenue: {amount}"))

        imported_count += 1

    conn.commit()

    return {
        "imported": imported_count,
        "missing": missing_products,
        "week_range": (last_mon, last_sun)
    }
