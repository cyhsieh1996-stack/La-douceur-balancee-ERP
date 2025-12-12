# logic/recipes_logic.py

from database.db import get_connection


# ------------------------------------------------------
# 取得某產品的食譜
# ------------------------------------------------------
def get_recipe(product_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT ri.id, rm.name, ri.amount, rm.unit,
               rm.id as material_id
        FROM recipe_items ri
        JOIN raw_materials rm ON rm.id = ri.material_id
        WHERE ri.product_id = ?
        ORDER BY rm.name ASC;
    """, (product_id,))

    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "recipe_id": r[0],
            "material_name": r[1],
            "amount": r[2],
            "unit": r[3],
            "material_id": r[4],
        })
    return result


# ------------------------------------------------------
# 新增食譜項目
# ------------------------------------------------------
def add_recipe_item(product_id, material_id, amount):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO recipe_items (product_id, material_id, amount)
        VALUES (?, ?, ?);
    """, (product_id, material_id, amount))

    conn.commit()
    conn.close()
    return True, "配方已新增"


# ------------------------------------------------------
# 刪除某項配方
# ------------------------------------------------------
def delete_recipe_item(recipe_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM recipe_items WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()

    return True, "配方已刪除"
