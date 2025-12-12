# logic/production_logic.py

from database.db import get_connection


# ------------------------------------------------------
# 檢查庫存是否足夠生產
# ------------------------------------------------------
def check_production_capacity(product_id, batch):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT rm.id, rm.name, rm.current_stock,
               ri.amount
        FROM recipe_items ri
        JOIN raw_materials rm ON rm.id = ri.material_id
        WHERE ri.product_id=?;
    """, (product_id,))

    rows = c.fetchall()
    conn.close()

    lack = []
    for r in rows:
        req = r[3] * batch
        if r[2] < req:
            lack.append({
                "name": r[1],
                "required": req,
                "current": r[2],
            })

    return lack  # 空代表可以生產


# ------------------------------------------------------
# 執行生產（扣庫存）
# ------------------------------------------------------
def produce(product_id, batch):
    lack = check_production_capacity(product_id, batch)
    if lack:
        return False, lack

    conn = get_connection()
    c = conn.cursor()

    # 扣庫存
    c.execute("""
        SELECT material_id, amount
        FROM recipe_items
        WHERE product_id=?;
    """, (product_id,))
    items = c.fetchall()

    for mat_id, amount in items:
        deduct = amount * batch
        c.execute("""
            UPDATE raw_materials
            SET current_stock = current_stock - ?
            WHERE id=?;
        """, (deduct, mat_id))

    # 紀錄生產
    c.execute("""
        INSERT INTO production_records (product_id, batch)
        VALUES (?, ?);
    """, (product_id, batch))

    conn.commit()
    conn.close()
    return True, "生產完成"
