#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SweetERP 成品匯入（最終分類版）
-----------------------------------------------------------
功能：
1. 從 item-overview + 商品排行 取出所有商品名稱（欄位：名稱）
2. 自動去重
3. 自動排除非甜點（咖啡、茶飲、酒、冰棒、永生花）
4. 自動分類甜點（14 類）
5. 自動解析口味（避免 I/O）
6. 自動判斷單位（個、盒、瓶、罐、袋、片）
7. 自動產生 item_id（類別2碼 + 口味2碼）
8. 將甜點寫入 SQLite (items 表)
9. 自動刪除「現存 items 中的非甜點」
10. 印出完整報告
"""

import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "database" / "sweet_erp.db"

# ============================================================
# 甜點分類（最終 14 類）
# ============================================================

CATEGORY_MAP = [
    ("費南雪", "FN", "費南雪"),
    ("瑪德蓮", "MD", "瑪德蓮"),
    ("戚風",   "GT", "戚風蛋糕"),
    ("軟餅",   "SC", "軟餅乾"),
    ("餅乾",   "SC", "餅乾"),
    ("塔皮",   "TA", "塔類"),
    ("塔",     "TA", "塔類"),
    ("布蕾",   "BL", "布蕾"),
    ("布朗尼", "BR", "布朗尼"),
    ("可麗露", "CL", "可麗露"),
    ("起司",   "CS", "起司蛋糕"),
    ("乳酪",   "CS", "乳酪蛋糕"),
    ("芝士",   "CS", "乳酪蛋糕"),
    ("提拉米蘇", "TM", "提拉米蘇"),
    ("巴斯克", "BK", "巴斯克"),
    ("生乳捲", "RL", "生乳捲"),
    ("蛋糕卷", "RL", "生乳捲"),
    ("磅蛋糕", "PC", "磅蛋糕"),
    ("蛋糕",   "CK", "蛋糕"),  # 最後匹配
]

# ============================================================
# 口味分類（避免 I, O）
# ============================================================

FLAVOR_MAP = [
    ("黑糖", "BK"),
    ("抹茶", "MT"),
    ("可可", "CC"),
    ("巧克力", "CC"),
    ("香草", "VA"),
    ("草莓", "SB"),
    ("蔓越莓", "CR"),
    ("芒果", "MG"),
    ("焦糖", "CM"),
]

DEFAULT_FLAVOR = "PN"

FORBIDDEN = set(["I", "O"])

# ============================================================
# 排除黑名單（不加入 ERP）
# ============================================================

EXCLUDE_KEYWORDS = [
    # 咖啡類
    "咖啡", "美式", "拿鐵", "歐蕾",
    # 茶類
    "紅茶", "奶茶", "烏龍", "翠玉", "白鷺", "綠茶",
    # 酒類
    "酒", "氣泡酒",
    # 冰品
    "冰棒", "冰淇淋",
    # 花 / 禮品
    "永生花", "花束",
]

# ============================================================
# 單位判斷
# ============================================================

UNIT_MAP = [
    ("禮盒", "盒"),
    ("盒", "盒"),
    ("瓶", "瓶"),
    ("罐", "罐"),
    ("袋", "袋"),
    ("片", "片"),
]

DEFAULT_UNIT = "個"

# ============================================================
# 工具函式
# ============================================================

def find_excel(keyword):
    for f in DATA_DIR.glob("*.xlsx"):
        if keyword in f.name:
            return f
    raise FileNotFoundError(f"找不到包含 {keyword} 的報表")


def safe_code_from_name(name):
    """
    若無法判斷口味：用中文轉兩碼代碼（避免 I, O）
    """
    if not name:
        return DEFAULT_FLAVOR

    chars = [c for c in name if c.strip()]
    chars = chars[:2] if chars else ["A", "A"]

    code = ""
    for ch in chars:
        val = ord(ch) % 26
        letter = chr(ord("A") + val)
        if letter in FORBIDDEN:
            letter = chr(ord("A") + ((val + 1) % 26))
        code += letter

    return code[:2]


def detect_category(name):
    for kw, code, label in CATEGORY_MAP:
        if kw in name:
            return code, label
    return None, None


def detect_flavor(name):
    for kw, code in FLAVOR_MAP:
        if kw in name:
            return code
    return safe_code_from_name(name)


def detect_unit(name):
    for kw, unit in UNIT_MAP:
        if kw in name:
            return unit
    return DEFAULT_UNIT


def ensure_unique_id(base, existing):
    if base not in existing:
        return base
    idx = 1
    while True:
        cand = f"{base}_{idx}"
        if cand not in existing:
            return cand
        idx += 1

# ============================================================
# 主程式：匯入成品
# ============================================================

def import_products():
    print("=== SweetERP 成品匯入（最終分類版） ===")

    if not DB_PATH.exists():
        raise FileNotFoundError("找不到資料庫")

    # 讀取兩份 Excel
    f1 = find_excel("item-overview")
    f2 = find_excel("商品排行")
    df1 = pd.read_excel(f1)
    df2 = pd.read_excel(f2)

    names = pd.concat([df1["名稱"], df2["名稱"]]).dropna().unique()
    names = [n.strip() for n in names if n.strip()]

    print(f"→ 報表總商品數：{len(names)}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ====================================================
    # 先清除資料庫內的非甜點
    # ====================================================
    print("\n=== 清除非甜點 ===")

    cur.execute("SELECT item_id, name FROM items")
    existing = cur.fetchall()

    delete_list = []

    for item_id, name in existing:
        if any(kw in name for kw in EXCLUDE_KEYWORDS):
            delete_list.append(item_id)

    for d in delete_list:
        cur.execute("DELETE FROM items WHERE item_id=?", (d,))

    print(f"→ 已刪除非甜點：{len(delete_list)} 筆")

    # ====================================================
    # 讀取刪除後的現存 items
    # ====================================================
    cur.execute("SELECT item_id, name FROM items")
    rows = cur.fetchall()
    existing_ids = {r[0] for r in rows}
    existing_names = {r[1] for r in rows}

    add_list = []
    skip_list = []
    exclude_list = []

    # ====================================================
    # 開始處理新商品
    # ====================================================
    for name in names:

        # 不要的
        if any(kw in name for kw in EXCLUDE_KEYWORDS):
            exclude_list.append(name)
            continue

        # 已存在就略過
        if name in existing_names:
            skip_list.append(name)
            continue

        # 嘗試分類甜點
        category_code, category_label = detect_category(name)
        if category_code is None:
            exclude_list.append(name)
            continue

        # 口味
        flavor_code = detect_flavor(name)

        # 單位
        unit = detect_unit(name)

        # 產生 item_id
        base_id = f"{category_code}{flavor_code}"
        item_id = ensure_unique_id(base_id, existing_ids)

        # 寫入 DB
        cur.execute(
            """
            INSERT INTO items
            (item_id, name, category, unit, type, track_stock, notes, cost, safety_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, name, category_label, unit, "finished", 1, None, None, None),
        )

        existing_ids.add(item_id)
        add_list.append(name)

    conn.commit()
    conn.close()

    # ====================================================
    # 結果報告
    # ====================================================
    print("\n=== 甜點匯入完成 ===")
    print(f"新增甜點：{len(add_list)} 筆")
    print(f"略過（已存在）：{len(skip_list)} 筆")
    print(f"排除（非甜點）：{len(exclude_list)} 筆")

    print("\n--- 新增項目 ---")
    for n in add_list:
        print(" +", n)

    print("\n--- 排除項目（非甜點） ---")
    for n in exclude_list:
        print(" -", n)


if __name__ == "__main__":
    import_products()
    print("\n完成！")
