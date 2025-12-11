# logic/raw_materials_logic.py

import sqlite3
from database.db import get_connection


# 取得全部原料（預設僅取 active 的）
def get_all_materials(include_inactive=False):
    conn = get_connection()
    c = conn.cursor()

    if include_inactive:
        c.execute("""
            SELECT id, name, brand, specification, unit, cost, current_stock, active, created_at
            FROM raw_materials
            ORDER BY name ASC;
        """)
    else:
        c.execute("""
            SELECT id, name, brand, specification, unit, cost, current_stock, active, created_at
            FROM raw_materials
            WHERE active = 1
            ORDER BY name ASC;
        """)

    rows = c.fetchall()
    conn.close()

    materials = []
    for r in rows:
        materials.append({
            "id": r[0],
            "name": r[1],
            "brand": r[2],
            "specification": r[3],
            "unit": r[4],
            "cost": r[5],
            "current_stock": r[6],
            "active": r[7],
            "created_at": r[8],
        })
    return materials


# 新增原料
def add_material(name, brand, specification, unit, cost):
    # 必填檢查
    if not name or not unit:
        return False, "原料名稱與單位為必填欄位。"

    # 成本若空白 → 設 0
    try:
        cost = float(cost) if cost else 0
    except ValueError:
        return False, "成本必須是數字。"

    conn = get_connection()
    c = conn.cursor()

    # 避免重複建立（同名 + 同品牌 + 同規格）
    c.execute("""
        SELECT COUNT(*) FROM raw_materials
        WHERE name = ? AND IFNULL(brand, '') = ? AND IFNULL(specification, '') = ? AND active = 1;
    """, (name, brand, specification))
    exists = c.fetchone()[0]

    if exists:
        conn.close()
        return False, "已存在相同名稱/品牌/規格的原料。"

    c.execute("""
        INSERT INTO raw_materials (name, brand, specification, unit, cost, current_stock, active)
        VALUES (?, ?, ?, ?, ?, 0, 1);
    """, (name, brand, specification, unit, cost))

    conn.commit()
    conn.close()

    return True, "原料已新增成功。"


# 編輯原料
def update_material(material_id, name, brand, specification, unit, cost):
    if not material_id:
        return False, "缺少原料 ID。"

    if not name or not unit:
        return False, "原料名稱與單位為必填欄位。"

    try:
        cost = float(cost) if cost else 0
    except ValueError:
        return False, "成本必須是數字。"

    conn = get_connection()
    c = conn.cursor()

    # 檢查重複（排除自己）
    c.execute("""
        SELECT COUNT(*) FROM raw_materials
        WHERE name = ? AND IFNULL(brand, '') = ? AND IFNULL(specification, '') = ? 
              AND id != ? AND active = 1;
    """, (name, brand, specification, material_id))

    exists = c.fetchone()[0]
    if exists:
        conn.close()
        return False, "已有相同名稱/品牌/規格的原料存在。"

    c.execute("""
        UPDATE raw_materials
        SET name = ?, brand = ?, specification = ?, unit = ?, cost = ?
        WHERE id = ?;
    """, (name, brand, specification, unit, cost, material_id))

    conn.commit()
    conn.close()

    return True, "原料資料已更新。"


# 刪除原料（soft delete，不破壞歷史入庫紀錄）
def delete_material(material_id):
    if not material_id:
        return False, "缺少 ID。"

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE raw_materials
        SET active = 0
        WHERE id = ?;
    """, (material_id,))

    conn.commit()
    conn.close()

    return True, "原料已刪除（停用）。"


# 取得單筆原料
def get_material_by_id(material_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, brand, specification, unit, cost, current_stock, active, created_at
        FROM raw_materials
        WHERE id = ?;
    """, (material_id,))

    r = c.fetchone()
    conn.close()

    if not r:
        return None

    return {
        "id": r[0],
        "name": r[1],
        "brand": r[2],
        "specification": r[3],
        "unit": r[4],
        "cost": r[5],
        "current_stock": r[6],
        "active": r[7],
        "created_at": r[8],
    }


# 🔽 入庫頁面會用到：提供下拉式選單
def get_material_dropdown_list():
    mats = get_all_materials(include_inactive=False)
    return [(m["id"], f"{m['name']}（{m['brand'] or ''}{m['specification'] or ''}）") for m in mats]
