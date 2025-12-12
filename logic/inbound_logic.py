# logic/inbound_logic.py

from database.db import get_connection


# ------------------------------------------------------
# 新增入庫紀錄 + 更新庫存
# ------------------------------------------------------
def add_inbound_record(material_id, qty, cost, supplier, note):
    try:
        qty = float(qty)
        cost = float(cost)
    except:
        return False, "數量與單價必須為數字"

    subtotal = qty * cost

    conn = get_connection()
    c = conn.cursor()

    # 新增入庫紀錄
    c.execute("""
        INSERT INTO inbound_records (material_id, qty, unit_cost, subtotal, supplier, note)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (material_id, qty, cost, subtotal, supplier, note))

    # 更新庫存
    c.execute("""
        UPDATE raw_materials
        SET current_stock = current_stock + ?
        WHERE id=?;
    """, (qty, material_id))

    conn.commit()
    conn.close()

    return True, "入庫已完成"


# ------------------------------------------------------
# 查詢全部入庫紀錄
# ------------------------------------------------------
def get_all_inbound_records():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT ir.id, rm.name, rm.brand, rm.spec,
               ir.qty, ir.unit_cost, ir.subtotal,
               ir.supplier, ir.note, ir.created_at
        FROM inbound_records ir
        JOIN raw_materials rm ON rm.id = ir.material_id
        ORDER BY ir.created_at DESC;
    """)

    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "brand": r[2],
            "spec": r[3],
            "qty": r[4],
            "unit_cost": r[5],
            "subtotal": r[6],
            "supplier": r[7],
            "note": r[8],
            "created_at": r[9],
        })
    return result
