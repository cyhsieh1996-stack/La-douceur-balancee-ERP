from database.db import get_db


def create_material_table():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            brand TEXT,
            vendor TEXT,
            unit TEXT,
            unit_price REAL DEFAULT 0,
            stock REAL DEFAULT 0,
            safe_stock REAL DEFAULT 50
        )
        """
    )
    conn.commit()
    conn.close()


def list_materials():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id, name, category, brand, vendor, unit, unit_price, stock, safe_stock
        FROM raw_materials
        ORDER BY id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_material(data: dict):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO raw_materials (name, category, brand, vendor, unit, unit_price, stock, safe_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name", ""),
            data.get("category", ""),
            data.get("brand", ""),
            data.get("vendor", "") or data.get("supplier", ""),
            data.get("unit", ""),
            float(data.get("unit_price", 0) or 0),
            float(data.get("stock", 0) or 0),
            float(data.get("safe_stock", 0) or 0),
        ),
    )
    conn.commit()
    conn.close()


def update_material(mid: int, data: dict):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE raw_materials
        SET name=?, category=?, brand=?, vendor=?, unit=?, unit_price=?, stock=?, safe_stock=?
        WHERE id=?
        """,
        (
            data.get("name", ""),
            data.get("category", ""),
            data.get("brand", ""),
            data.get("vendor", "") or data.get("supplier", ""),
            data.get("unit", ""),
            float(data.get("unit_price", 0) or 0),
            float(data.get("stock", 0) or 0),
            float(data.get("safe_stock", 0) or 0),
            mid,
        ),
    )
    conn.commit()
    conn.close()


def delete_material(mid: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM raw_materials WHERE id=?", (mid,))
    conn.commit()
    conn.close()
