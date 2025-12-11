from database.db import get_connection
from logic.inventory_logic import get_inventory_summary


# -----------------------------------------------------
# 建立盤點調整紀錄
# -----------------------------------------------------
def record_adjustment(date, item_id, system_qty, physical_qty):
    diff = physical_qty - system_qty

    conn = get_connection()
    cursor = conn.cursor()

    # 寫入 monthly_adjustments
    cursor.execute(
        """
        INSERT INTO monthly_adjustments
        (date, item_id, system_qty, physical_qty, diff)
        VALUES (?, ?, ?, ?, ?)
        """,
        (date, item_id, system_qty, physical_qty, diff)
    )
    adjust_id = cursor.lastrowid

    # 建立調整出入庫
    if diff > 0:
        # 實際 > 帳面 → 補庫
        cursor.execute(
            """
            INSERT INTO stock_movements
            (date, item_id, type, qty_in, qty_out, reference_doc, notes)
            VALUES (?, ?, 'Adjust', ?, 0, ?, '盤點調整 增加')
            """,
            (date, item_id, diff, f"ADJ-{adjust_id}")
        )
    elif diff < 0:
        # 實際 < 帳面 → 扣庫
        cursor.execute(
            """
            INSERT INTO stock_movements
            (date, item_id, type, qty_in, qty_out, reference_doc, notes)
            VALUES (?, ?, 'Adjust', 0, ?, ?, '盤點調整 減少')
            """,
            (date, item_id, abs(diff), f"ADJ-{adjust_id}")
        )

    conn.commit()
    conn.close()

    return adjust_id


# -----------------------------------------------------
# 列出所有盤點紀錄
# -----------------------------------------------------
def list_adjustments():
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT ma.*, items.name AS item_name, items.unit
        FROM monthly_adjustments ma
        JOIN items ON items.item_id = ma.item_id
        ORDER BY date DESC, id DESC
        """
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


# -----------------------------------------------------
# 提供給 UI：取得帳面庫存（system_qty）
# -----------------------------------------------------
def get_system_inventory_dict():
    """回傳 { item_id: qty } 給 UI 快速查詢"""
    inv = get_inventory_summary()
    return {row["item_id"]: row["qty"] for row in inv}
