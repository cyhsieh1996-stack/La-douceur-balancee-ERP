# ui/pages/dashboard_page.py

import customtkinter as ctk
from tkinter import ttk

from logic.dashboard_logic import (
    get_total_materials,
    get_total_products,
    get_low_stock_materials,
    get_recent_inbound
)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="儀表板", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        # ======== 上方 KPI 區塊 ========
        kpi_frame = ctk.CTkFrame(self)
        kpi_frame.pack(fill="x", padx=20)

        # 原料總數
        total_materials = get_total_materials()
        self.kpi1 = ctk.CTkLabel(kpi_frame, text=f"原料數量：{total_materials}", font=ctk.CTkFont(size=18))
        self.kpi1.grid(row=0, column=0, padx=20, pady=10)

        # 產品總數
        total_products = get_total_products()
        self.kpi2 = ctk.CTkLabel(kpi_frame, text=f"產品種類：{total_products}", font=ctk.CTkFont(size=18))
        self.kpi2.grid(row=0, column=1, padx=20, pady=10)

        # ======== 庫存不足警示 ========
        section1_title = ctk.CTkLabel(self, text="⚠ 庫存不足的原料", font=ctk.CTkFont(size=20, weight="bold"))
        section1_title.pack(pady=(30, 10))

        low_frame = ctk.CTkFrame(self)
        low_frame.pack(fill="both", padx=20, pady=10)

        low_cols = ("id", "name", "current", "safe")
        self.low_table = ttk.Treeview(low_frame, columns=low_cols, show="headings", height=5)

        self.low_table.heading("id", text="ID")
        self.low_table.heading("name", text="原料")
        self.low_table.heading("current", text="庫存")
        self.low_table.heading("safe", text="安全庫存")

        self.low_table.pack(fill="both", expand=True)
        self.load_low_stock()

        # ======== 最近入庫紀錄 ========
        section2_title = ctk.CTkLabel(self, text="最近入庫紀錄", font=ctk.CTkFont(size=20, weight="bold"))
        section2_title.pack(pady=(30, 10))

        inbound_frame = ctk.CTkFrame(self)
        inbound_frame.pack(fill="both", padx=20, pady=10, expand=True)

        inbound_cols = ("id", "name", "qty", "cost", "subtotal", "time")
        self.inbound_table = ttk.Treeview(inbound_frame, columns=inbound_cols, show="headings", height=8)

        for col, text in zip(inbound_cols, ["ID", "原料", "數量", "單價", "小計", "時間"]):
            self.inbound_table.heading(col, text=text)

        self.inbound_table.pack(fill="both", expand=True)
        self.load_inbound()

    # ===================================
    # 載入庫存不足資料
    # ===================================
    def load_low_stock(self):
        for row in self.low_table.get_children():
            self.low_table.delete(row)

        for item in get_low_stock_materials():
            self.low_table.insert(
                "",
                "end",
                values=(item["id"], item["name"], item["current_stock"], item["safe_stock"])
            )

    # ===================================
    # 載入最近入庫資料
    # ===================================
    def load_inbound(self):
        for row in self.inbound_table.get_children():
            self.inbound_table.delete(row)

        for r in get_recent_inbound():
            self.inbound_table.insert(
                "",
                "end",
                values=(r["id"], r["name"], r["qty"], r["cost"], r["subtotal"], r["time"])
            )
