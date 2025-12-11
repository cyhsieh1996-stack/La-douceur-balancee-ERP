import sqlite3
from database.db import get_connection

def create_material_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS material_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            supplier TEXT,
            vendor_code TEXT,
            spec TEXT,
            unit TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def list_materials():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM material_master ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


def add_material(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO material_master 
        (code, name, brand, supplier, vendor_code, spec, unit, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))
    """, (
        data["code"],
        data["name"],
        data.get("brand", ""),
        data.get("supplier", ""),
        data.get("vendor_code", ""),
        data.get("spec", ""),
        data.get("unit", "")
    ))

    conn.commit()
    conn.close()


def update_material(mid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE material_master SET
            code=?, name=?, brand=?, supplier=?, vendor_code=?, spec=?, unit=?
        WHERE id=?
    """, (
        data["code"], data["name"], data.get("brand",""), data.get("supplier",""),
        data.get("vendor_code",""), data.get("spec",""), data.get("unit",""), mid
    ))

    conn.commit()
    conn.close()


def delete_material(mid: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM material_master WHERE id=?", (mid,))
    conn.commit()
    conn.close()
