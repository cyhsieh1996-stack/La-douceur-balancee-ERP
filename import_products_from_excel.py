#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pandas as pd

from database.db import get_db, init_db


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

EXCLUDE_KEYWORDS = [
    "咖啡", "美式", "拿鐵", "歐蕾",
    "紅茶", "奶茶", "烏龍", "翠玉", "白鷺", "綠茶",
    "酒", "氣泡酒",
    "冰棒", "冰淇淋",
    "永生花", "花束",
]


def find_excel(keyword):
    for file_path in DATA_DIR.glob("*.xlsx"):
        if keyword in file_path.name:
            return file_path
    raise FileNotFoundError(f"找不到包含 {keyword} 的報表")


def load_product_names():
    overview = pd.read_excel(find_excel("item-overview"))
    ranking = pd.read_excel(find_excel("商品排行"))
    names = pd.concat([overview["名稱"], ranking["名稱"]]).dropna().unique()
    return [str(name).strip() for name in names if str(name).strip()]


def infer_category(name):
    mapping = [
        ("費南雪", "費南雪"),
        ("瑪德蓮", "瑪德蓮"),
        ("戚風", "戚風蛋糕"),
        ("軟餅", "軟餅乾"),
        ("餅乾", "餅乾"),
        ("塔", "塔類"),
        ("布蕾", "布蕾"),
        ("布朗尼", "布朗尼"),
        ("可麗露", "可麗露"),
        ("起司", "起司蛋糕"),
        ("乳酪", "乳酪蛋糕"),
        ("提拉米蘇", "提拉米蘇"),
        ("巴斯克", "巴斯克"),
        ("生乳捲", "生乳捲"),
        ("磅蛋糕", "磅蛋糕"),
        ("蛋糕", "蛋糕"),
    ]
    for keyword, label in mapping:
        if keyword in name:
            return label
    return "其他"


def import_products():
    print("=== SweetERP 成品匯入（現行 products 表） ===")
    init_db()
    names = load_product_names()
    print(f"→ 報表總商品數：{len(names)}")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products")
    existing_names = {row["name"] for row in cur.fetchall()}

    added = []
    skipped = []
    excluded = []

    for name in names:
        if any(keyword in name for keyword in EXCLUDE_KEYWORDS):
            excluded.append(name)
            continue
        if name in existing_names:
            skipped.append(name)
            continue

        cur.execute(
            """
            INSERT INTO products (name, category, price, cost, stock, shelf_life)
            VALUES (?, ?, 0, 0, 0, NULL)
            """,
            (name, infer_category(name)),
        )
        existing_names.add(name)
        added.append(name)

    conn.commit()
    conn.close()

    print(f"新增成品：{len(added)} 筆")
    print(f"略過重複：{len(skipped)} 筆")
    print(f"排除非甜點：{len(excluded)} 筆")


if __name__ == "__main__":
    import_products()
