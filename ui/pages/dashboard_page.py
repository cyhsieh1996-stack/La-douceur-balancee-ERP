import customtkinter as ctk
from logic.dashboard_logic import (
    get_week_sales_kpi,
    get_top3_products_week,
    get_low_stock_items,
    get_recent_lots,
)


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        title = ctk.CTkLabel(self, text="SweetERP Dashboard", font=("Arial", 24))
        title.pack(pady=15)

        # KPI 區塊
        self.kpi_frame = ctk.CTkFrame(self)
        self.kpi_frame.pack(fill="x", padx=20, pady=10)

        self.kpi_label = ctk.CTkLabel(self.kpi_frame, text="", font=("Arial", 18))
        self.kpi_label.pack(pady=10)

        # Top 3 銷售
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=20, pady=10)

        self.top_label = ctk.CTkLabel(self.top_frame, text="", font=("Arial", 16))
        self.top_label.pack(pady=10)

        # 低庫存
        self.low_frame = ctk.CTkFrame(self)
        self.low_frame.pack(fill="x", padx=20, pady=10)

        self.low_label = ctk.CTkLabel(self.low_frame, text="", font=("Arial", 16))
        self.low_label.pack(pady=10)

        # 最新批號
        self.lot_frame = ctk.CTkFrame(self)
        self.lot_frame.pack(fill="x", padx=20, pady=10)

        self.lot_label = ctk.CTkLabel(self.lot_frame, text="", font=("Arial", 16))
        self.lot_label.pack(pady=10)

        self.refresh_dashboard()

    # ============================================================
    # 更新整個 Dashboard 資料
    # ============================================================
    def refresh_dashboard(self):
        # 本週 KPI
        qty, amt = get_week_sales_kpi()
        self.kpi_label.configure(
            text=f"本週銷售：{qty} 件　｜　銷售額：${amt:,.0f}"
        )

        # Top 3
        top3 = get_top3_products_week()
        if top3:
            text = "本週 Top 3:\n" + "\n".join(
                [f"{t['name']}（{t['qty']} 件）" for t in top3]
            )
        else:
            text = "尚無銷售資料"
        self.top_label.configure(text=text)

        # Low stock
        lows = get_low_stock_items()
        if lows:
            text = "低庫存警示：\n" + "\n".join(
                [f"{i['name']}：{i['stock']}（安全庫存 {i['safety']}）" for i in lows]
            )
        else:
            text = "沒有低庫存品項"
        self.low_label.configure(text=text)

        # Recent LOTs
        lots = get_recent_lots()
        if lots:
            text = "最近生產批次：\n" + "\n".join(
                [f"{l['date']}｜{l['name']} {l['qty']} 件｜LOT {l['lot']}" for l in lots]
            )
        else:
            text = "尚無生產紀錄"
        self.lot_label.configure(text=text)
