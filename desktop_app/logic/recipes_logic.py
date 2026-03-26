from database.db import get_db

def ensure_recipe_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            qty_per_unit REAL NOT NULL,
            note TEXT,
            UNIQUE(product_id, material_id),
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(material_id) REFERENCES raw_materials(id)
        )
        """
    )
    conn.commit()
    conn.close()

def get_recipe_items(product_id):
    ensure_recipe_table()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            r.id,
            r.product_id,
            r.material_id,
            m.name AS material_name,
            m.unit AS unit,
            m.stock AS current_stock,
            r.qty_per_unit,
            r.note
        FROM product_recipes r
        JOIN raw_materials m ON r.material_id = m.id
        WHERE r.product_id = ?
        ORDER BY m.name COLLATE NOCASE ASC
        """,
        (product_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_recipe_item(product_id, material_id, qty_per_unit, note=""):
    ensure_recipe_table()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            return False, "找不到產品"

        cursor.execute("SELECT id FROM raw_materials WHERE id = ?", (material_id,))
        if not cursor.fetchone():
            return False, "找不到原料"

        cursor.execute(
            """
            INSERT INTO product_recipes (product_id, material_id, qty_per_unit, note)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(product_id, material_id)
            DO UPDATE SET qty_per_unit = excluded.qty_per_unit, note = excluded.note
            """,
            (product_id, material_id, qty_per_unit, note),
        )
        conn.commit()
        return True, "配方已儲存"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def delete_recipe_item(recipe_id):
    ensure_recipe_table()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM product_recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        return True, "配方項目已刪除"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_recipe_usage_preview(product_id, production_qty):
    ensure_recipe_table()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            r.id,
            r.material_id,
            m.name AS material_name,
            m.unit AS unit,
            m.stock AS current_stock,
            r.qty_per_unit,
            (r.qty_per_unit * ?) AS required_qty,
            (m.stock - (r.qty_per_unit * ?)) AS remaining_stock,
            r.note
        FROM product_recipes r
        JOIN raw_materials m ON r.material_id = m.id
        WHERE r.product_id = ?
        ORDER BY m.name COLLATE NOCASE ASC
        """,
        (production_qty, production_qty, product_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
