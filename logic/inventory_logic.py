import sqlite3
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
