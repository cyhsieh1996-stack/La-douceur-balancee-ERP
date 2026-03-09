from database.db import get_db
from logic.inventory_logic import adjust_stock, ensure_inventory_table


def record_adjustment(date, material_id, system_qty, physical_qty):
    diff = physical_qty - system_qty
    reason = f"月結盤點調整 ({date})"
    success, msg = adjust_stock(material_id, physical_qty, reason)
    if not success:
        raise RuntimeError(msg)
    return {"material_id": material_id, "diff": diff}


def list_adjustments():
    ensure_inventory_table()
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT
            a.id,
            a.date,
            a.material_id,
            m.name AS item_name,
            a.old_stock AS system_qty,
            a.new_stock AS physical_qty,
            a.diff,
            m.unit
        FROM inventory_adjustments a
        JOIN raw_materials m ON m.id = a.material_id
        WHERE a.reason LIKE '月結盤點調整%'
        ORDER BY a.date DESC, a.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_system_inventory_dict():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT id, stock
        FROM raw_materials
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()
    return {str(row["id"]): row["stock"] for row in rows}


def list_items():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT id, name, unit
        FROM raw_materials
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
