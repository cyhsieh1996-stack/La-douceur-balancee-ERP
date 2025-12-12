import customtkinter as ctk
from tkinter import ttk
from logic.dashboard_logic import (
    get_total_material_stock,
    get_total_product_stock,
    get_low_stock_materials
)


class DashboardPage(ctk.CTkFrame):
    """ SweetERP 儀表板（ACTgene 風格 + 適合甜點店配色） """

    def __init__(self, master):
        super().__init__(master, fg_color="#F5F5F5")  # 整體背景

        # ------------------------------------------------------
        # 標題列
        # ------------------------------------------------------
        title_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=6)
        title_bar.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_bar,
            text="SweetERP 儀表板 Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#333333"
        )
        title_label.pack(padx=20, pady=15)

        # ------------------------------------------------------
        # 左右主區塊（仿 ACTgene）
        # ------------------------------------------------------
        main_area = ctk.CTkFrame(self, fg_color="#F5F5F5")
        main_area.pack(fill="both", expand=True, padx=20, pady=10)

        # 左區塊：KPI 模組
        left_panel = ctk.CTkFrame(main_area, fg_color="#FFFFFF", corner_radius=6, border_width=1, border_color="#D6D6D6")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # 右區塊：低庫存提示
        right_panel = ctk.CTkFrame(main_area, fg_color="#FFFFFF", corner_radius=6, border_width=1, border_color="#D6D6D6")
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # ------------------------------------------------------
        # 左區：KPI 區
        # ------------------------------------------------------
        kpi_title = ctk.CTkLabel(
            left_panel, text="今日概況・KPI 指標",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#444444"
        )
        kpi_title.pack(pady=15)

        # 取得資料
        total_material = get_total_material_stock()
        total_product = get_total_product_stock()

        # KPI 卡片外框
        kpi_frame = ctk.CTkFrame(left_panel, fg_color="#F5F5F5", corner_radius=6)
        kpi_frame.pack(fill="x", padx=20, pady=10)

        # K1：原料總庫存
        k1 = self.build_kpi_card(kpi_frame, "原料庫存容量", total_material, "#C9986C")
        k1.grid(row=0, column=0, padx=10, pady=10)

        # K2：產品庫存容量
        k2 = self.build_kpi_card(kpi_frame, "產品庫存容量", total_product, "#E8C7A3")
        k2.grid(row=0, column=1, padx=10, pady=10)

        # ------------------------------------------------------
        # 右區：低庫存警示
        # ------------------------------------------------------
        warn_title = ctk.CTkLabel(
            right_panel, text="⚠ 低庫存原料警示",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#C75C5C"
        )
        warn_title.pack(pady=15)

        warn_frame = ctk.CTkFrame(right_panel, fg_color="#FFFFFF")
        warn_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Treeview
        columns = ("name", "stock", "unit")
        table = ttk.Treeview(warn_frame, columns=columns, show="headings", height=10)
        table.heading("name", text="原料名稱")
        table.heading("stock", text="目前庫存")
        table.heading("unit", text="單位")
        table.pack(fill="both", expand=True)

        # 載入資料
        low_list = get_low_stock_materials()
        for m in low_list:
            table.insert("", "end", values=(m["name"], m["stock"], m["unit"]))

    # ------------------------------------------------------
    # KPI 卡片
    # ------------------------------------------------------
    def build_kpi_card(self, master, title, value, color):
        frame = ctk.CTkFrame(master, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#D6D6D6")

        label_title = ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#555555"
        )
        label_title.pack(pady=(10, 0))

        label_value = ctk.CTkLabel(
            frame, text=str(value),
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=color
        )
        label_value.pack(pady=(5, 15))

        return frame
