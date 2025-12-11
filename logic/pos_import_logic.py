import pandas as pd
from database.db import get_db
from datetime import datetime, timedelta
import sqlite3

# ---------------------------------------------------------
# 工具：從項目 excel 匯入，寫入 sales_header / sales_detail / stock_movements
# ---------------------------------------------------------

def import_pos_item_overview(file_path):
    """
    iCHEF 的商品銷售明細，用於建立:
    - sales_detail
    - sales_header
    - stock_movements (Sale)
    """

    df = pd.read_excel(file_path)

    conn = get_db()
    cursor = conn.cursor()

    # 找出日期（iCHEF 每筆都有日期）
    # 假設欄位名稱包含 Date / 日期
    possible_cols = [c for c in df.columns if "日期" in c or "date" in c.lower()]
    if not possible_cols:
        raise ValueError("Excel 無法辨識日期欄位")
    date_col = possible_cols[0]

    # 找週期：計算匯入前完整一週（週一～週日）
    import_date = datetime.now().date()
    last_sun = import_date - timedelta(days=import_date.weekday() + 1)
    last_mon = last_sun - timedelta(days=6)

    # 過濾上一週資料
    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    target = df[(df[date_col] >= last_mon) & (df[date_col] <= last_sun)]

    if target.empty:
        return f"資料無上一週 {last_mon}～{last_sun} 的紀錄"

    # 建立 sales_header
    total_sales = float(target["小計"].sum()) if "小計" in df.columns else 0.0
    cursor.execute(
        """
        INSERT INTO sales_header (date, total_amount, source)
        VALUES (?, ?, ?)
        """,
        (str(last_sun), total_sales, "iCHEF")
    )
    header_id = cursor.lastrowid

    # 建立 sales_detail + stock_movements
    for _, row in target.iterrows():
        name = row["品名"] if "品名" in row else None
        qty = row["數量"] if "數量" in row else 0
        amount = row["小計"] if "小計" in row else 0

        # 找 item_id
        cursor.execute("SELECT item_id FROM items WHERE name = ?", (name,))
        found = cursor.fetchone()
        if not found:
            continue
        item_id = found[0]

        # sales_detail
        cursor.execute(
            """
            INSERT INTO sales_detail (header_id, date, item_id, qty, line_amount)
            VALUES (?, ?, ?, ?, ?)
            """,
            (header_id, str(last_sun), item_id, qty, amount)
        )

        # stock_movements (Sale)
        cursor.execute(
            """
            INSERT INTO stock_movements (date, item_id, type, qty_out)
            VALUES (?, ?, 'Sale', ?)
            """,
            (str(last_sun), item_id, qty)
        )

    conn.commit()

    return f"匯入成功：上一週 {last_mon}～{last_sun} 共 {len(target)} 筆資料"


# ---------------------------------------------------------
# 給 UI 用的總匯入函式（UI 叫這個）
# ---------------------------------------------------------
def import_pos_weekly_data(item_overview_path, _closing_summary_path=None):
    """
    UI 的 POS 匯入頁會叫這個函式。
    目前先只處理商品銷售明細（item overview）。
    """
    result = import_pos_item_overview(item_overview_path)
    return result
