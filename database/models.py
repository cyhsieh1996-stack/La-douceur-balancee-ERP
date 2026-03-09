from logic.inventory_logic import adjust_stock
from logic.raw_materials_logic import get_all_materials


def insert_material(data):
    from database.material_master import add_material

    payload = {
        "name": data.get("原料名稱") or data.get("品名（中文）") or data.get("name", ""),
        "category": data.get("類別", ""),
        "brand": data.get("廠牌", ""),
        "vendor": data.get("廠商") or data.get("供應商", ""),
        "unit": data.get("單位") or data.get("重量單位（g / ml / pcs）", ""),
        "unit_price": data.get("單價", 0),
        "safe_stock": data.get("安全庫存", 0),
    }
    add_material(payload)


def list_materials():
    return get_all_materials()


def adjust_inventory(material_id, new_qty):
    return adjust_stock(material_id, new_qty, "盤點重設為實際量")


def insert_inventory_log(material_id, change, note):
    materials = get_all_materials()
    material = next((m for m in materials if m["id"] == material_id), None)
    if not material:
        return False, "找不到原料"
    new_qty = float(material["stock"]) + float(change)
    return adjust_stock(material_id, new_qty, note)
