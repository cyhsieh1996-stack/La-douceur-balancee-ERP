# logic/inbound_logic.py

from database.db import get_connection
from logic.raw_materials_logic import get_material_by_id


# 產生入庫流水號
def generate_inbound_code():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM inbound_records;")
    count = c.fetchone()[0] + 1

    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")

    return f"IB{date_str}-{count:04d}"


# 新增入庫紀錄
def add_inbound_record(material_id, qty, unit_cost, supplier, note):
    try:
        qty = float(qty)
        unit_cost = float(unit_cost)
    except ValueError:
        return False, "數量與單價必須是數字"

    if qty <= 0:
        return False, "入庫數量必須大於 0"

    subtotal = qty * unit_cost

    conn = get_connection()
    c = conn.cursor()

    inbound_code = generate_inbound_code()

    # 寫入 inbound_records
    c.execute("""
        INSERT INTO inbound_records (material_id, qty, unit_cost, subtotal, supplier, note)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (material_id, qty, unit_cost, subtotal, supplier, note))

    # 更新原料庫存（加總）
    c.execute("""
        UPDATE raw_materials
        SET current_stock = current_stock + ?
        WHERE id = ?;
    """, (qty, material_id))

    conn.commit()
    conn.close()

    return True, "入庫成功"


# 查詢完整入庫紀錄列表（提供給 UI 顯示）
def get_all_inbound_records():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT ir.id, ir.material_id, rm.name, rm.brand, rm.specification,
               ir.qty, ir.unit_cost, ir.subtotal, ir.supplier, ir.note, ir.created_at
        FROM inbound_records ir
        JOIN raw_materials rm ON rm.id = ir.material_id
        ORDER BY ir.created_at DESC;
    """)

    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "material_id": r[1],
            "name": r[2],
            "brand": r[3],
            "spec": r[4],
            "qty": r[5],
            "unit_cost": r[6],
            "subtotal": r[7],
            "supplier": r[8],
            "note": r[9],
            "created_at": r[10],
        })

    return results
