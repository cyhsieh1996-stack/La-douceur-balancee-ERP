import customtkinter as ctk
from tkinter import ttk
from logic.inventory_logic import get_inventory_list


class InventoryPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="庫存狀態",
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20)

        columns = ("id", "name", "brand", "spec",
                   "unit", "current_stock", "safe_stock", "status")

        self.table = ttk.Treeview(frame, columns=columns, show="headings")

        headers = ["ID", "原料", "廠牌", "規格", "單位", "庫存量", "安全量", "狀態"]
        for c, h in zip(columns, headers):
            self.table.heading(c, text=h)

        self.table.pack(fill="both", expand=True)

        self.load_inventory()

    def load_inventory(self):
        for r in self.table.get_children():
            self.table.delete(r)

        data = get_inventory_list()

        for m in data:
            status = "正常"
            if m["current_stock"] < m["safe_stock"]:
                status = "⚠ 庫存不足"

            self.table.insert("", "end", values=(
                m["id"],
                m["name"],
                m["brand"],
                m["spec"],
                m["unit"],
                m["current_stock"],
                m["safe_stock"],
                status,
            ))
