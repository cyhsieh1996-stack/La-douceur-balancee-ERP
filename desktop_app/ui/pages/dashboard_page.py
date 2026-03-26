import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from ui.theme import Color, Font
from logic.dashboard_logic import (
    get_workspace_summary,
    get_low_stock_materials, get_expiring_products, get_expiring_raw_materials,
    get_top_selling_products,
    get_recent_production, get_recent_inbound
)
from logic.export_logic import export_all_data

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, fg_color="transparent")
        self.navigate = navigate

        header_frame = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=18, border_width=1, border_color=Color.BORDER)
        header_frame.pack(fill="x", pady=(0, 18))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=18)
        ctk.CTkLabel(title_box, text="今日作業工作台", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(
            title_box,
            text="先看警示、再開始作業，常用流程可以直接從這裡進入。",
            font=Font.BODY,
            text_color=Color.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 0))

        action_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_box.pack(side="right", padx=20, pady=18)
        ctk.CTkButton(
            action_box,
            text="重新整理",
            fg_color=Color.GRAY_BUTTON,
            hover_color=Color.GRAY_BUTTON_HOVER,
            text_color=Color.TEXT_DARK,
            width=100,
            height=36,
            command=self.refresh_dashboard,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            action_box,
            text="匯出資料",
            fg_color=Color.INFO,
            width=110,
            height=36,
            command=self.handle_export,
        ).pack(side="left")

        self.workspace_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_panel.pack(fill="x", pady=(0, 20))
        self.workspace_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.summary_cards = {}
        self.create_summary_card("待補貨原料", "low_stock_count", "低於安全庫存的原料筆數", 0, 0)
        self.create_summary_card("即將到期批號", "expiring_total", "7 天成品 + 30 天原料", 0, 1)
        self.create_summary_card("本月銷售額", "month_sales_amount", "依 POS 匯入銷售資料計算", 0, 2)
        self.create_summary_card("今日作業筆數", "today_activity_total", "入庫 + 生產 + POS 匯入", 0, 3)

        self.quick_panel = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=16, border_width=1, border_color=Color.BORDER)
        self.quick_panel.pack(fill="x", pady=(0, 20))
        self.quick_panel.grid_columnconfigure((0, 1), weight=1)
        self.create_quick_actions()

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self.content_frame.columnconfigure((0, 1, 2), weight=1)
        self.content_frame.rowconfigure((0, 1), weight=1)

        self.create_table_section(self.content_frame, "🏆 熱銷產品排行", ["排名", "產品名稱", "銷量"], [50, 160, 70], 0, 0, "tree_top3")
        self.create_table_section(self.content_frame, "📥 最近入庫紀錄", ["時間", "原料", "數量", "單位"], [100, 120, 60, 50], 0, 1, "tree_rec_inbound")
        self.create_table_section(self.content_frame, "⚠️ 原料即將過期", ["效期", "名稱", "批號"], [90, 110, 80], 0, 2, "tree_exp_mat")

        self.create_table_section(self.content_frame, "🚨 原料缺貨警報", ["名稱", "目前", "安全", "單位"], [100, 60, 60, 50], 1, 0, "tree_low_stock")
        self.create_table_section(self.content_frame, "👩‍🍳 最近生產紀錄", ["時間", "產品", "數量", "批號"], [100, 120, 60, 80], 1, 1, "tree_rec_prod")
        self.create_table_section(self.content_frame, "⏳ 成品即將過期", ["效期", "產品", "批號"], [90, 120, 90], 1, 2, "tree_exp_prod")

        self.refresh_dashboard()

    def create_summary_card(self, title, key, hint, row, col):
        card = ctk.CTkFrame(self.workspace_panel, fg_color=Color.WHITE_CARD, corner_radius=16, border_width=1, border_color=Color.BORDER)
        card.grid(row=row, column=col, padx=8, pady=0, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(anchor="w", padx=16, pady=(14, 6))
        value_label = ctk.CTkLabel(card, text="0", font=Font.STAT_NUMBER, text_color=Color.PRIMARY)
        value_label.pack(anchor="w", padx=16)
        hint_label = ctk.CTkLabel(card, text=hint, font=Font.SMALL, text_color=Color.TEXT_LIGHT)
        hint_label.pack(anchor="w", padx=16, pady=(4, 14))
        self.summary_cards[key] = value_label

    def create_quick_actions(self):
        left = ctk.CTkFrame(self.quick_panel, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        right = ctk.CTkFrame(self.quick_panel, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        ctk.CTkLabel(left, text="今日優先作業", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w")
        self.priority_label = ctk.CTkLabel(
            left,
            text="系統正在整理今日工作摘要。",
            font=Font.BODY,
            text_color=Color.TEXT_BODY,
            justify="left",
            wraplength=360,
        )
        self.priority_label.pack(anchor="w", pady=(8, 12))

        action_grid = ctk.CTkFrame(right, fg_color="transparent")
        action_grid.pack(fill="x")
        action_grid.grid_columnconfigure((0, 1, 2), weight=1)

        actions = [
            ("開始入庫", "原料入庫與批號登錄", "inbound", Color.PRIMARY),
            ("開始生產", "建立今日批次", "production", "#0F766E"),
            ("庫存調整", "修正盤點差異", "inventory", "#B45309"),
            ("匯入 POS", "載入今日銷售", "pos_import", "#7C3AED"),
            ("新增原料", "維護原料主檔", "raw_materials", "#475569"),
            ("新增產品", "維護產品主檔", "products", "#BE185D"),
        ]

        for idx, (title, subtitle, page_name, color) in enumerate(actions):
            row, col = divmod(idx, 3)
            self.create_action_button(action_grid, title, subtitle, page_name, color, row, col)

    def create_action_button(self, parent, title, subtitle, page_name, color, row, col):
        btn = ctk.CTkButton(
            parent,
            text=f"{title}\n{subtitle}",
            fg_color=color,
            hover_color=color,
            corner_radius=14,
            height=82,
            font=Font.BODY_BOLD,
            command=lambda: self.go_to(page_name),
        )
        btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

    def handle_export(self):
        folder = filedialog.askdirectory(title="選擇匯出儲存位置")
        if not folder: return
        success, msg = export_all_data(folder)
        if success: messagebox.showinfo("成功", msg)
        else: messagebox.showerror("失敗", msg)

    def go_to(self, page_name):
        if self.navigate:
            self.navigate(page_name)

    def create_table_section(self, parent, title, headers, widths, row, col, attr_name):
        container = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=14, border_width=1, border_color=Color.BORDER)
        container.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        header_box = ctk.CTkFrame(container, fg_color="transparent", height=40)
        header_box.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(header_box, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(side="left")
        
        table_frame = ctk.CTkFrame(container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=2, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="white", 
                        foreground=Color.TEXT_DARK, 
                        rowheight=38, 
                        font=Font.SMALL, 
                        fieldbackground="white", 
                        borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#E5E7EB", foreground=Color.TEXT_DARK, relief="flat")
        
        tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=11)
        
        for col_name, w in zip(headers, widths):
            tree.heading(col_name, text=col_name)
            tree.column(col_name, width=w, minwidth=40, anchor="center", stretch=True)
        
        tree.tag_configure('odd', background='white')
        tree.tag_configure('even', background="#F9FAFB")
        
        tree.pack(side="left", fill="both", expand=True, padx=5)
        setattr(self, attr_name, tree)

    def refresh_dashboard(self):
        summary = get_workspace_summary()
        expiring_total = summary["expiring_products_count"] + summary["expiring_materials_count"]
        today_activity_total = summary["today_inbound_count"] + summary["today_production_count"] + summary["today_sales_count"]

        self.summary_cards["low_stock_count"].configure(text=str(summary["low_stock_count"]))
        self.summary_cards["expiring_total"].configure(text=str(expiring_total))
        self.summary_cards["month_sales_amount"].configure(text=f"${self.smart_format(summary['month_sales_amount'])}")
        self.summary_cards["today_activity_total"].configure(text=str(today_activity_total))

        priority_lines = [
            f"待補貨原料 {summary['low_stock_count']} 筆，建議先看庫存警報。",
            f"即將到期批號 {expiring_total} 筆，包含成品 {summary['expiring_products_count']}、原料 {summary['expiring_materials_count']}。",
            f"今日已登錄入庫 {summary['today_inbound_count']} 筆、生產 {summary['today_production_count']} 筆、POS {summary['today_sales_count']} 筆。",
            f"目前主檔共有原料 {summary['materials_count']} 筆、產品 {summary['products_count']} 筆。",
        ]
        self.priority_label.configure(text="\n".join(priority_lines))

        self.update_tree(self.tree_low_stock, get_low_stock_materials(), [0, 1, 2, 3])

        tops = get_top_selling_products(limit=12)
        self.update_tree_custom(self.tree_top3, tops)
        
        self.update_tree(self.tree_exp_prod, get_expiring_products(), [2, 0, 1])
        self.update_tree(self.tree_exp_mat, get_expiring_raw_materials(), [2, 0, 1])

        prod_logs = get_recent_production(limit=12)
        self.update_tree(self.tree_rec_prod, prod_logs, [0, 1, 2, 3]) 

        inbound_logs = get_recent_inbound(limit=12)
        self.update_tree(self.tree_rec_inbound, inbound_logs, [0, 1, 2, 3])

    def smart_format(self, value):
        try:
            f = float(value)
            if f.is_integer(): return int(f)
            return round(f, 2)
        except: return value

    def update_tree(self, tree, data, indices):
        for item in tree.get_children(): tree.delete(item)
        if not data: return
        for i, row in enumerate(data):
            vals = []
            for idx in indices:
                val = row[idx]
                if isinstance(val, str) and len(val) > 16 and "-" in val:
                    val = val[:10]
                vals.append(self.smart_format(val))
            
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.insert("", "end", values=vals, tags=(tag,))

    def update_tree_custom(self, tree, data):
        for item in tree.get_children(): tree.delete(item)
        if not data: return
        for i, row in enumerate(data):
            tag = 'even' if i % 2 == 0 else 'odd'
            qty = self.smart_format(row[1])
            tree.insert("", "end", values=(f"No.{i+1}", row[0], qty), tags=(tag,))
