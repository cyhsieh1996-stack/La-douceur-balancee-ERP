from datetime import datetime
from database.db import get_db

def ensure_inventory_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(inventory_adjustments)")
    columns = {row[1] for row in cursor.fetchall()}

    if not columns:
        cursor.execute("""
            CREATE TABLE inventory_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,
                old_stock REAL NOT NULL,
                new_stock REAL NOT NULL,
                diff REAL NOT NULL,
                reason TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(material_id) REFERENCES raw_materials(id)
            )
        """)
    elif {"change_qty", "action_type", "note"}.issubset(columns):
        cursor.execute("""
            CREATE TABLE inventory_adjustments_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,
                old_stock REAL NOT NULL DEFAULT 0,
                new_stock REAL NOT NULL DEFAULT 0,
                diff REAL NOT NULL,
                reason TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(material_id) REFERENCES raw_materials(id)
            )
        """)
        cursor.execute("""
            INSERT INTO inventory_adjustments_new (id, material_id, old_stock, new_stock, diff, reason, date)
            SELECT
                id,
                material_id,
                0,
                0,
                change_qty,
                COALESCE(note, action_type, ''),
                COALESCE(date, CURRENT_TIMESTAMP)
            FROM inventory_adjustments
        """)
        cursor.execute("DROP TABLE inventory_adjustments")
        cursor.execute("ALTER TABLE inventory_adjustments_new RENAME TO inventory_adjustments")

    conn.commit()
    conn.close()

def adjust_stock(material_id, new_stock, reason):
    ensure_inventory_table()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock FROM raw_materials WHERE id = ?", (material_id,))
        row = cursor.fetchone()
        if not row: return False, "找不到該原料"
        
        old_stock = row[0]
        new_stock = float(new_stock)
        diff = new_stock - old_stock
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO inventory_adjustments (material_id, old_stock, new_stock, diff, reason, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (material_id, old_stock, new_stock, diff, reason, date_str))

        cursor.execute("UPDATE raw_materials SET stock = ? WHERE id = ?", (new_stock, material_id))
        conn.commit()
        return True, "庫存調整完成"
    except Exception as e:
        conn.rollback()
        return False, f"調整失敗: {str(e)}"
    finally:
        conn.close()

def get_inventory_summary():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM raw_materials")
    material_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM raw_materials WHERE stock < safe_stock AND safe_stock > 0")
    low_stock_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM raw_materials WHERE stock <= 0")
    zero_stock_count = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COALESCE(SUM(stock * unit_price), 0) FROM raw_materials")
    estimated_stock_value = cursor.fetchone()[0] or 0

    conn.close()
    return {
        "material_count": material_count,
        "low_stock_count": low_stock_count,
        "zero_stock_count": zero_stock_count,
        "estimated_stock_value": estimated_stock_value,
    }

def get_inventory_snapshot(keyword="", low_stock_only=False):
    conn = get_db()
    cursor = conn.cursor()

    conditions = []
    params = []

    if keyword:
        conditions.append("(name LIKE ? OR category LIKE ? OR vendor LIKE ? OR brand LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like, like, like])

    if low_stock_only:
        conditions.append("stock < safe_stock AND safe_stock > 0")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    cursor.execute(
        f"""
        SELECT
            id,
            name,
            category,
            brand,
            vendor,
            unit,
            unit_price,
            stock,
            safe_stock,
            stock - safe_stock AS balance_to_safe
        FROM raw_materials
        {where_clause}
        ORDER BY
            CASE WHEN safe_stock > 0 AND stock < safe_stock THEN 0 ELSE 1 END,
            name COLLATE NOCASE ASC
        """,
        params,
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_adjustments(limit=20):
    ensure_inventory_table()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.date, m.name, a.old_stock, a.new_stock, a.diff, m.unit, a.reason
        FROM inventory_adjustments a
        JOIN raw_materials m ON a.material_id = m.id
        ORDER BY a.date DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_material_stock(material_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stock, unit FROM raw_materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, "")
