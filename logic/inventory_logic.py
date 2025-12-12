# logic/inventory_logic.py

from logic.raw_materials_logic import get_all_materials


def get_inventory_list():
    return get_all_materials()
