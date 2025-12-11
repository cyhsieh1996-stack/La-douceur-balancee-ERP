import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "sweet_erp.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def init_db():
    print("Initializing SweetERP v1.0 database...")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing DB removed.")

    conn = sqlite3.connect(DB_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()
    conn.close()

    print("SweetERP database created successfully:", DB_PATH)


if __name__ == "__main__":
    init_db()
