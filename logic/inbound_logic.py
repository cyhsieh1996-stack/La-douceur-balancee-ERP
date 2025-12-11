from database.db import get_db

# 進貨登錄
def record_inbound(item_id, qty, unit_cost, notes=""):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stock_movements (date, item_id, type, qty_in, qty_out, notes)
        VALUES (DATE('now'), ?, 'Purchase', ?, 0, ?)
    """, (item_id, qty, notes))

    # 更新最新成本
    cursor.execute("""
        UPDATE items
        SET cost = ?
        WHERE item_id = ?
    """, (unit_cost, item_id))

    conn.commit()


# 查詢所有進貨紀錄（依時間排序）
def list_inbound_records():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, date, item_id, qty_in, notes
        FROM stock_movements
        WHERE type = 'Purchase'
        ORDER BY date DESC
    """).fetchall()

    return [
        {
            "id": r[0],
            "date": r[1],
            "item_id": r[2],
            "qty": r[3],
            "notes": r[4]
        }
        for r in rows
    ]
