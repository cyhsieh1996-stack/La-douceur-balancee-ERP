from database.db import get_db

# =========================================================
# 取得某成品的所有食譜項目（原料清單）
# =========================================================
def get_recipe(product_id):
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT r.id, r.material_id, i.name AS material_name, r.qty, r.unit
        FROM recipes r
        JOIN items i ON i.item_id = r.material_id
        WHERE r.product_id = ?
        ORDER BY i.category, material_name
    """, (product_id,)).fetchall()

    return [dict(r) for r in rows]


# =========================================================
# 新增一筆食譜項目
# =========================================================
def add_recipe_item(product_id, material_id, qty, unit):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO recipes (product_id, material_id, qty, unit)
        VALUES (?, ?, ?, ?)
    """, (product_id, material_id, qty, unit))

    conn.commit()


# =========================================================
# 修改食譜中的某個原料
# =========================================================
def update_recipe_item(recipe_id, qty, unit):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE recipes
        SET qty = ?, unit = ?
        WHERE id = ?
    """, (qty, unit, recipe_id))

    conn.commit()


# =========================================================
# 刪除食譜中的某個原料
# =========================================================
def delete_recipe_item(recipe_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM recipes
        WHERE id = ?
    """, (recipe_id,))

    conn.commit()


# =========================================================
# 生產扣料用：取得某成品的「原料 + 用量」
# =========================================================
def get_materials_for_production(product_id):
    """
    回傳格式：
    [
        { material_id: "BU01", qty: 15, unit: "g" },
        ...
    ]
    """
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT material_id, qty, unit
        FROM recipes
        WHERE product_id = ?
    """, (product_id,)).fetchall()

    return [dict(r) for r in rows]
