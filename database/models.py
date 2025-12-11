from database.db import get_connection

# ----------------------------------------
# 新增原料
# ----------------------------------------
def insert_material(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO materials 
        (code, name_ch, name_en, brand, supplier, supplier_code, package_spec, weight_unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["原料編號（自訂）"],
        data["品名（中文）"],
        data["品名（英文，可留空）"],
        data["廠牌"],
        data["供應商"],
        data["廠商料號"],
        data["包裝規格（如 1000g / 罐）"],
        data["重量單位（g / ml / pcs）"]
    ))

    material_id = cur.lastrowid
    cur.execute("INSERT INTO inventory (material_id, qty) VALUES (?, 0)", (material_id,))
    conn.commit()
    conn.close()

# ----------------------------------------
# 取得全部原料
# ----------------------------------------
def list_materials():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM materials ORDER BY id")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

# ----------------------------------------
# 庫存調整（盤點）
# ----------------------------------------
def adjust_inventory(material_id, new_qty):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE inventory SET qty=? WHERE material_id=?", (new_qty, material_id))
    cur.execute("""
        INSERT INTO inventory_log (material_id, change, note)
        VALUES (?, ?, ?)
    """, (material_id, new_qty, "盤點重設為實際量"))

    conn.commit()
    conn.close()

# ----------------------------------------
# 記錄異動
# ----------------------------------------
def insert_inventory_log(material_id, change, note):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO inventory_log (material_id, change, note)
        VALUES (?, ?, ?)
    """, (material_id, change, note))

    cur.execute("""
        UPDATE inventory 
        SET qty = qty + ?
        WHERE material_id = ?
    """, (change, material_id))

    conn.commit()
    conn.close()
