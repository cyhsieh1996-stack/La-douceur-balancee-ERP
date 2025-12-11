# logic/materials_logic.py
from database.db import get_connection, now_str


def list_materials():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM material_master ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_material(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO material_master
        (code, name_zh, name_en, brand, vendor, vendor_code, spec, unit, note,
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("code"),
        data.get("name_zh"),
        data.get("name_en"),
        data.get("brand"),
        data.get("vendor"),
        data.get("vendor_code"),
        data.get("spec"),
        data.get("unit"),
        data.get("note"),
        now_str(),
        now_str(),
    ))

    conn.commit()
    conn.close()


def update_material(id, data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE material_master
        SET code=?, name_zh=?, name_en=?, brand=?, vendor=?, vendor_code=?,
            spec=?, unit=?, note=?, updated_at=?
        WHERE id=?
    """, (
        data.get("code"),
        data.get("name_zh"),
        data.get("name_en"),
        data.get("brand"),
        data.get("vendor"),
        data.get("vendor_code"),
        data.get("spec"),
        data.get("unit"),
        data.get("note"),
        now_str(),
        id
    ))

    conn.commit()
    conn.close()


def delete_material(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM material_master WHERE id=?", (id,))
    conn.commit()
    conn.close()
