from database.db import get_db


def list_all_items():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT CAST(id AS TEXT) AS item_id, name, category, unit, 'raw' AS type, safe_stock AS safety_stock
        FROM raw_materials
        UNION ALL
        SELECT CAST(id AS TEXT) AS item_id, name, category, '' AS unit, 'finished' AS type, NULL AS safety_stock
        FROM products
        ORDER BY category, name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_finished_items():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT CAST(id AS TEXT) AS item_id, name, category, '' AS unit, NULL AS safety_stock
        FROM products
        ORDER BY category, name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_raw_materials():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT CAST(id AS TEXT) AS item_id, name, category, unit, safe_stock AS safety_stock
        FROM raw_materials
        ORDER BY category, name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_item_by_name(name):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT CAST(id AS TEXT) AS item_id, name, category, '' AS unit, 'finished' AS type
        FROM products
        WHERE name = ?
        """,
        (name,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT CAST(id AS TEXT) AS item_id, name, category, unit, 'raw' AS type
        FROM raw_materials
        WHERE id = ?
        UNION ALL
        SELECT CAST(id AS TEXT) AS item_id, name, category, '' AS unit, 'finished' AS type
        FROM products
        WHERE id = ?
        LIMIT 1
        """,
        (item_id, item_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_item(item_id, name, category, unit, type, safety_stock=None, notes=""):
    conn = get_db()
    cursor = conn.cursor()
    if type == "raw":
        cursor.execute(
            """
            INSERT INTO raw_materials (name, category, unit, safe_stock)
            VALUES (?, ?, ?, ?)
            """,
            (name, category, unit, safety_stock or 0),
        )
    else:
        cursor.execute(
            """
            INSERT INTO products (name, category, price, cost, stock, shelf_life)
            VALUES (?, ?, 0, 0, 0, NULL)
            """,
            (name, category),
        )
    conn.commit()
    conn.close()


def update_item(item_id, name, category, unit, safety_stock=None, notes=""):
    conn = get_db()
    cursor = conn.cursor()
    updated = cursor.execute(
        """
        UPDATE raw_materials
        SET name=?, category=?, unit=?, safe_stock=?
        WHERE id=?
        """,
        (name, category, unit, safety_stock or 0, item_id),
    )
    if updated.rowcount == 0:
        cursor.execute(
            """
            UPDATE products
            SET name=?, category=?
            WHERE id=?
            """,
            (name, category, item_id),
        )
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM raw_materials WHERE id=?", (item_id,))
    if cursor.rowcount == 0:
        cursor.execute("DELETE FROM products WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
