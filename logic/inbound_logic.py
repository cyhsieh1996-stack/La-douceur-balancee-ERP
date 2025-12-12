# inbound_logic.py
from database.db import get_db


# ==========================================
# 新增入庫紀錄（並更新原料庫存）
# ==========================================
def add_inbound_record(material_id, qty, date, note=""):
    if not material_id or not qty:
        return False, "請輸入完整資料"

    conn = get_db()
    cur = conn.cursor()

    # 新增入庫紀錄
    cur.execute("""
        INSERT INTO inbound_records (material_id, qty, date, note)
        VALUES (?, ?, ?, ?);
    """, (material_id, qty, date, note))

    # 更新原料庫存
    cur.execute("""
        UPDATE raw_materials
        SET stock = stock + ?
        WHERE id = ?;
    """, (qty, material_id))

    conn.commit()
    return True, "入庫成功"


# ==========================================
# 取得所有入庫紀錄
# ==========================================
def get_all_inbound_records():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT ir.id, rm.name, ir.qty, ir.date, ir.note
        FROM inbound_records ir
        JOIN raw_materials rm ON ir.material_id = rm.id
        ORDER BY ir.date DESC;
    """)

    rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "material_name": r[1],
            "qty": r[2],
            "date": r[3],
            "note": r[4]
        }
        for r in rows
    ]
