import customtkinter as ctk
from logic.dashboard_logic import (
    get_total_materials,
    get_total_products,
    get_low_stock_materials,
    get_weekly_sales,
)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="SweetERP 儀表板",
                              font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        # KPI 區塊
        kpi_frame = ctk.CTkFrame(self)
        kpi_frame.pack(pady=10, fill="x", padx=20)

        self.kpi_materials = ctk.CTkLabel(
            kpi_frame, text="", font=ctk.CTkFont(size=18))
        self.kpi_materials.grid(row=0, column=0, padx=20, pady=10)

        self.kpi_products = ctk.CTkLabel(
            kpi_frame, text="", font=ctk.CTkFont(size=18))
        self.kpi_products.grid(row=0, column=1, padx=20, pady=10)

        self.kpi_sales = ctk.CTkLabel(
            kpi_frame, text="", font=ctk.CTkFont(size=18))
        self.kpi_sales.grid(row=0, column=2, padx=20, pady=10)

        # 庫存不足區塊
        low_frame = ctk.CTkFrame(self)
        low_frame.pack(pady=20, fill="both", expand=True, padx=20)

        low_title = ctk.CTkLabel(
            low_frame, text="庫存不足警示", font=ctk.CTkFont(size=20, weight="bold"))
        low_title.pack(pady=10)

        self.low_list = ctk.CTkTextbox(low_frame, height=200)
        self.low_list.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_data()

    # --------------------------------------------------
    # 更新儀表板資料
    # --------------------------------------------------
    def refresh_data(self):
        total_m = get_total_materials()
        total_p = get_total_products()
        week_sales = get_weekly_sales()
        low_stock = get_low_stock_materials()

        self.kpi_materials.configure(text=f"原料種類：{total_m}")
        self.kpi_products.configure(text=f"產品種類：{total_p}")
        self.kpi_sales.configure(text=f"本週銷售額：${week_sales:,.0f}")

        self.low_list.delete("1.0", "end")

        if not low_stock:
            self.low_list.insert("end", "目前所有原料庫存充足 😊")
        else:
            for item in low_stock:
                self.low_list.insert(
                    "end",
                    f"{item['name']}：庫存 {item['current_stock']} / 安全量 {item['safe_stock']}\n"
                )
