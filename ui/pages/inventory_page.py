# ui/pages/inventory_page.py

import customtkinter as ctk
from tkinter import ttk
from logic.raw_materials_logic import get_all_materials


class InventoryPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="庫存狀態", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "name", "brand", "spec", "current_stock", "safe_stock", "status")

        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.table.heading("id", text="ID")
        self.table.heading("name", text="原料")
        self.table.heading("brand", text="廠牌")
        self.table.heading("spec", text="規格")
        self.table.heading("current_stock", text="庫存量")
        self.table.heading("safe_stock", text="安全庫存")
        self.table.heading("status", text="狀態")

        self.table.pack(fill="both", expand=True)

        self.load_inventory()

    # ------------------------------------------------------
    # 載入庫存資料
    # ------------------------------------------------------
    def load_inventory(self):
        for row in self.table.get_children():
            self.table.delete(row)

        materials = get_all_materials()

        for m in materials:
            status = "正常"
            if m["current_stock"] < m["safe_stock"]:
                status = "⚠ 庫存不足"

            self.table.insert(
                "",
                "end",
                values=(
                    m["id"],
                    m["name"],
                    m["brand"],
                    m["spec"],
                    m["current_stock"],
                    m["safe_stock"],
                    status
                )
            )
