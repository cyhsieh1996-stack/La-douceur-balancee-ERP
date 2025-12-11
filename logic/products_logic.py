from database.db import get_db

# =========================================================
# 取得所有成品（type = 'finished'）
# =========================================================
def get_all_products():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT *
        FROM items
        WHERE type = 'finished'
        ORDER BY category, name
    """).fetchall()

    return [dict(r) for r in rows]


# =========================================================
# 新增成品
# =========================================================
def add_product(item_id, name, category, unit, notes="", safety_stock=None):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (item_id, name, category, unit, type, track_stock, notes, safety_stock)
        VALUES (?, ?, ?, ?, 'finished', 1, ?, ?)
    """, (item_id, name, category, unit, notes, safety_stock))

    conn.commit()


# =========================================================
# 更新成品
# =========================================================
def update_product(item_id, name, category, unit, notes="", safety_stock=None):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET name=?, category=?, unit=?, notes=?, safety_stock=?
        WHERE item_id=? AND type='finished'
    """, (name, category, unit, notes, safety_stock, item_id))

    conn.commit()


# =========================================================
# 刪除成品
# =========================================================
def delete_product(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM items
        WHERE item_id=? AND type='finished'
    """, (item_id,))

    conn.commit()


# =========================================================
# 依分類取得成品
# =========================================================
def get_products_by_category(category):
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT *
        FROM items
        WHERE type='finished' AND category=?
        ORDER BY name
    """, (category,)).fetchall()

    return [dict(r) for r in rows]


# =========================================================
# 取得單一商品
# =========================================================
def get_product(item_id):
    conn = get_db()
    cursor = conn.cursor()

    row = cursor.execute("""
        SELECT *
        FROM items
        WHERE item_id=? AND type='finished'
    """, (item_id,)).fetchone()

    return dict(row) if row else None
