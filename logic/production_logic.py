from datetime import datetime
from database.db import get_db
from .recipes_logic import get_materials_for_production


# =========================================================
# LOT Number 產生邏輯
# =========================================================
def generate_lot_number(product_id):
    today = datetime.now()
    year = today.strftime("%y")
    week = today.strftime("%V")   # ISO 週次
    weekday = today.isoweekday()  # 1~7

    return f"{year}{week}{weekday}{product_id}"


# =========================================================
# 生產（建立成品 + 扣除原料自動化）
# =========================================================
def produce_product(product_id, qty_output):
    """
    qty_output = 生產的成品數量（個、份等）
    """

    conn = get_db()
    cursor = conn.cursor()

    # 產生 LOT 編號
    lot_number = generate_lot_number(product_id)

    # 1️⃣ 成品入庫：Production_Output
    cursor.execute("""
        INSERT INTO stock_movements (date, item_id, type, qty_in, qty_out, lot_number)
        VALUES (DATE('now'), ?, 'Production_Output', ?, 0, ?)
    """, (product_id, qty_output, lot_number))

    # 2️⃣ 自動扣除原料
    materials = get_materials_for_production(product_id)

    for m in materials:
        material_id = m["material_id"]
        required_qty = m["qty"] * qty_output   # EX：每份 15g → 生產30份→450g
        unit = m["unit"]

        cursor.execute("""
            INSERT INTO stock_movements (date, item_id, type, qty_in, qty_out, notes)
            VALUES (DATE('now'), ?, 'Production_Consume', 0, ?, ?)
        """, (material_id, required_qty, f"Used in LOT {lot_number}"))

    conn.commit()

    return lot_number
