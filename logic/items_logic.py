from database.db import get_db

# ============================================================
# 共用：取得所有 items
# ============================================================
def list_all_items():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT item_id, name, category, unit, type, safety_stock
        FROM items
        ORDER BY category, name
    """).fetchall()
    return [dict(r) for r in rows]


# ============================================================
# 成品（Finished Products）
# ============================================================
def list_finished_items():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT item_id, name, category, unit, safety_stock
        FROM items
        WHERE type='finished'
        ORDER BY category, name
    """).fetchall()
    return [dict(r) for r in rows]


# ============================================================
# 原料（Raw Materials）
# ============================================================
def list_raw_materials():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT item_id, name, category, unit, safety_stock
        FROM items
        WHERE type='raw'
        ORDER BY category, name
    """).fetchall()
    return [dict(r) for r in rows]


# ============================================================
# 依名稱找 item（POS 匯入用）
# ============================================================
def get_item_by_name(name):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT *
        FROM items
        WHERE name = ?
    """, (name,)).fetchone()
    return dict(row) if row else None


# ============================================================
# 依 item_id 找商品
# ============================================================
def get_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT *
        FROM items
        WHERE item_id = ?
    """, (item_id,)).fetchone()
    return dict(row) if row else None


# ============================================================
# 新增 Item（包含原料或成品）
# ============================================================
def add_item(item_id, name, category, unit, type, safety_stock=None, notes=""):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (item_id, name, category, unit, type, safety_stock, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (item_id, name, category, unit, type, safety_stock, notes))

    conn.commit()


# ============================================================
# 更新 Item
# ============================================================
def update_item(item_id, name, category, unit, safety_stock=None, notes=""):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET name=?, category=?, unit=?, safety_stock=?, notes=?
        WHERE item_id=?
    """, (name, category, unit, safety_stock, notes, item_id))

    conn.commit()


# ============================================================
# 刪除 Item
# ============================================================
def delete_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE item_id=?", (item_id,))
    conn.commit()
