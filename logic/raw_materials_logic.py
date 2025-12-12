# raw_materials_logic.py
from database.db import get_db


# ==========================================
# 取得所有原料（完整資料）
# ==========================================
def get_all_materials():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, brand, unit, stock, safe_stock
        FROM raw_materials
        ORDER BY name ASC;
    """)

    rows = cur.fetchall()
    return [dict(row) for row in rows]


# ==========================================
# 提供下拉式選單使用的原料清單
# ==========================================
def get_material_dropdown_list():
    """
    回傳格式：
    [
        {"id": 1, "name": "鮮奶"},
        {"id": 2, "name": "砂糖"},
        ...
    ]
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM raw_materials ORDER BY name ASC;")
    rows = cur.fetchall()

    return [{"id": r[0], "name": r[1]} for r in rows]


# ==========================================
# 新增原料
# ==========================================
def add_material(name, brand, unit, safe_stock=50):
    if not name:
        return False, "原料名稱不可空白"

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO raw_materials (name, brand, unit, stock, safe_stock)
        VALUES (?, ?, ?, 0, ?);
    """, (name, brand, unit, safe_stock))

    conn.commit()
    return True, "原料已新增"


# ==========================================
# 更新原料
# ==========================================
def update_material(material_id, name, brand, unit, safe_stock):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE raw_materials
        SET name = ?, brand = ?, unit = ?, safe_stock = ?
        WHERE id = ?;
    """, (name, brand, unit, safe_stock, material_id))

    conn.commit()
    return True, "原料資料已更新"


# ==========================================
# 刪除原料
# ==========================================
def delete_material(material_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM raw_materials WHERE id = ?", (material_id,))
    conn.commit()

    return True, "原料已刪除"
