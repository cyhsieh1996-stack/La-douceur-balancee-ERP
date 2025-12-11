from database.db import get_db

# =========================================================
# 取得所有原料（type = 'raw'）
# =========================================================
def get_all_raw_materials():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT *
        FROM items
        WHERE type = 'raw'
        ORDER BY name
    """).fetchall()

    return [dict(r) for r in rows]


# =========================================================
# 新增原料
# =========================================================
def add_raw_material(item_id, name, category, unit, track_stock, notes, cost, safety_stock):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (item_id, name, category, unit, type, track_stock, notes, cost, safety_stock)
        VALUES (?, ?, ?, ?, 'raw', ?, ?, ?, ?)
    """, (item_id, name, category, unit, track_stock, notes, cost, safety_stock))

    conn.commit()


# =========================================================
# 更新原料資料
# =========================================================
def update_raw_material(item_id, name, category, unit, track_stock, notes, cost, safety_stock):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET name=?, category=?, unit=?, track_stock=?, notes=?, cost=?, safety_stock=?
        WHERE item_id=? AND type='raw'
    """, (name, category, unit, track_stock, notes, cost, safety_stock, item_id))

    conn.commit()


# =========================================================
# 刪除原料（僅允許刪除 type='raw'）
# =========================================================
def delete_raw_material(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM items
        WHERE item_id=? AND type='raw'
    """, (item_id,))

    conn.commit()


# =========================================================
# 取得單一原料資料
# =========================================================
def get_raw_material(item_id):
    conn = get_db()
    cursor = conn.cursor()

    row = cursor.execute("""
        SELECT *
        FROM items
        WHERE item_id=? AND type='raw'
    """, (item_id,)).fetchone()

    return dict(row) if row else None


# =========================================================
# 更新原料成本（用於進貨時更新最新價格）
# =========================================================
def update_raw_material_cost(item_id, new_cost):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET cost=?
        WHERE item_id=? AND type='raw'
    """, (new_cost, item_id))

    conn.commit()
