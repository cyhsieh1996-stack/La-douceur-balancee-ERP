# logic/raw_materials_logic.py

from database.db import get_connection


# ------------------------------------------------------
# 新增原料
# ------------------------------------------------------
def add_material(name, brand, spec, unit, safe_stock):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO raw_materials (name, brand, spec, unit, safe_stock, current_stock)
        VALUES (?, ?, ?, ?, ?, 0);
    """, (name, brand, spec, unit, safe_stock))

    conn.commit()
    conn.close()
    return True, "原料已新增"


# ------------------------------------------------------
# 取得全部原料（完整資料）
# ------------------------------------------------------
def get_all_materials():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, brand, spec, unit, safe_stock, current_stock, active
        FROM raw_materials
        WHERE active = 1
        ORDER BY name ASC;
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
            "unit": r[4],
            "safe_stock": r[5],
            "current_stock": r[6],
            "active": r[7],
        })
    return result


# ------------------------------------------------------
# 下拉選單用資料
# ------------------------------------------------------
def get_material_dropdown_list():
    materials = get_all_materials()
    return [(m["id"], f"{m['name']} ({m['brand'] or ''}{m['spec'] or ''})") for m in materials]


# ------------------------------------------------------
# 更新原料資料
# ------------------------------------------------------
def update_material(mat_id, name, brand, spec, unit, safe_stock):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE raw_materials
        SET name=?, brand=?, spec=?, unit=?, safe_stock=?
        WHERE id=?;
    """, (name, brand, spec, unit, safe_stock, mat_id))

    conn.commit()
    conn.close()
    return True, "原料已更新"


# ------------------------------------------------------
# 刪除（停用）原料
# ------------------------------------------------------
def delete_material(mat_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE raw_materials SET active=0 WHERE id=?", (mat_id,))
    conn.commit()
    conn.close()

    return True, "原料已刪除"
