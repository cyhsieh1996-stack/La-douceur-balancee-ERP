import customtkinter as ctk
from logic.reports_logic import (
    get_inventory_report,
    get_cost_report,
    get_sales_ranking,
    get_gross_margin_report,
    get_payment_report,
)


class ReportsPage(ctk.CTkFrame):
    """報表中心"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="#F7F4EF")

        title = ctk.CTkLabel(
            self,
            text="📈 報表中心（Reports Center）",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#4A4A48",
        )
        title.pack(anchor="w", padx=25, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="查看銷售、成本、毛利、庫存報告",
            font=ctk.CTkFont(size=15),
            text_color="#6B6B6A",
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))

        # 主框
        container = ctk.CTkFrame(self, fg_color="#EFECE7", corner_radius=12)
        container.pack(fill="both", expand=True, padx=25, pady=20)

        # 左側按鈕欄
        side = ctk.CTkFrame(container, fg_color="#F7F4EF", corner_radius=10, width=220)
        side.pack(side="left", fill="y", padx=15, pady=15)

        btns = [
            ("庫存現況報表", self.show_inventory),
            ("成品成本報表", self.show_cost),
            ("銷售排行報表", self.show_ranking),
            ("毛利報表", self.show_margin),
            ("支付方式報表", self.show_payment),
        ]

        for label, func in btns:
            ctk.CTkButton(
                side,
                text=label,
                command=func,
                corner_radius=6,
                fg_color="#D8D2C4",
                hover_color="#C7C1B4",
                text_color="#4A4A48",
            ).pack(fill="x", padx=15, pady=8)

        # 右側結果區
        self.result_frame = ctk.CTkScrollableFrame(
            container, fg_color="#F7F4EF", corner_radius=10
        )
        self.result_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

    # ---------------------------------------------------
    # 報表渲染
    # ---------------------------------------------------

    def clear_result(self):
        for w in self.result_frame.winfo_children():
            w.destroy()

    def render_rows(self, rows):
        self.clear_result()
        if not rows:
            ctk.CTkLabel(self.result_frame, text="無資料", text_color="#4A4A48").pack(pady=10)
            return

        for r in rows:
            text = "｜".join(f"{k}: {v}" for k, v in r.items())
            row = ctk.CTkLabel(
                self.result_frame,
                text=text,
                justify="left",
                text_color="#4A4A48"
            )
            row.pack(anchor="w", padx=10, pady=5)

    def show_inventory(self):
        rows = get_inventory_report()
        self.render_rows(rows)

    def show_cost(self):
        rows = get_cost_report()
        self.render_rows(rows)

    def show_ranking(self):
        rows = get_sales_ranking()
        self.render_rows(rows)

    def show_margin(self):
        rows = get_gross_margin_report()
        self.render_rows(rows)

    def show_payment(self):
        rows = get_payment_report()
        self.render_rows(rows)
