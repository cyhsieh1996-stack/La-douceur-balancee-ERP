import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from ui.theme import Color, Font, Layout
from logic.dashboard_logic import (
    get_low_stock_materials, get_expiring_products, get_expiring_raw_materials,
    get_top_selling_products, get_monthly_finance, get_dashboard_summary
)
from logic.export_logic import export_all_data

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 標題區
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header_frame, text="主儀表板 Dashboard", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(side="left")
        
        btn_export = ctk.CTkButton(header_frame, text="📥 匯出資料備份", fg_color=Color.INFO, width=120, height=Layout.BTN_HEIGHT, command=self.handle_export)
        btn_export.pack(side="right")

        # 財務數據區 (兩排)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 15))
        self.stats_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # 本月
        self.card_rev_this = self.create_stat_card(self.stats_frame, "本月營業額", "$0", 0, Color.SUCCESS)
        self.card_cost_this = self.create_stat_card(self.stats_frame, "本月進貨成本", "$0", 1, Color.DANGER)
        
        # 上月
        self.card_rev_last = self.create_stat_card(self.stats_frame, "上月營業額", "$0", 2, Color.TEXT_LIGHT)
        self.card_cost_last = self.create_stat_card(self.stats_frame, "上月進貨成本", "$0", 3, Color.TEXT_LIGHT)

        # 下方資訊區 (三欄)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.columnconfigure((0, 1, 2), weight=1)

        self.create_left_panel(self.content_frame)
        self.create_center_panel(self.content_frame)
        self.create_right_panel(self.content_frame)

        self.refresh_dashboard()

    def handle_export(self):
        folder = filedialog.askdirectory(title="選擇匯出儲存位置")
        if not folder: return
        success, msg = export_all_data(folder)
        if success: messagebox.showinfo("成功", msg)
        else: messagebox.showerror("失敗", msg)

    def create_stat_card(self, parent, title, value, col, value_color=Color.TEXT_DARK):
        card = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=8)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        ctk.CTkLabel(card, text=title, font=Font.STAT_LABEL, text_color=Color.TEXT_LIGHT).pack(pady=(15, 2))
        lbl = ctk.CTkLabel(card, text=value, font=Font.STAT_NUMBER, text_color=value_color)
        lbl.pack(pady=(0, 15))
        return lbl

    def create_left_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, padx=5, sticky="nsew")
        self.create_table_section(frame, "🚨 原料缺貨警報", ["名稱", "目前", "安全", "單位"], [120, 60, 60, 50], "tree_low_stock")
        self.create_table_section(frame, "⚠️ 原料即將過期", ["效期", "名稱", "批號"], [100, 120, 80], "tree_exp_mat")

    def create_center_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=1, padx=5, sticky="nsew")
        self.create_table_section(frame, "🏆 本月熱銷 Top 3", ["排名", "產品名稱", "銷量"], [60, 180, 80], "tree_top3")

    def create_right_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=2, padx=5, sticky="nsew")
        self.create_table_section(frame, "⏳ 成品即將過期", ["效期", "產品", "批號"], [100, 120, 100], "tree_exp_prod")

    def create_table_section(self, parent, title, headers, widths, attr_name):
        container = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=8)
        container.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(container, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(anchor="w", padx=15, pady=(10, 5))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")
        
        tree = ttk.Treeview(container, columns=headers, show="headings", height=5)
        for col, w in zip(headers, widths):
            tree.heading(col, text=col); tree.column(col, width=w, anchor="center")
        
        tree.tag_configure('odd', background='white'); tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        tree.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        setattr(self, attr_name, tree)

    def refresh_dashboard(self):
        # 1. 財務數據 (已在 Logic 層轉整數)
        fin = get_monthly_finance()
        self.card_rev_this.configure(text=f"${fin['this_month']['revenue']:,}")
        self.card_cost_this.configure(text=f"${fin['this_month']['cost']:,}")
        self.card_rev_last.configure(text=f"${fin['last_month']['revenue']:,}")
        self.card_cost_last.configure(text=f"${fin['last_month']['cost']:,}")
        
        # 2. 表格更新 (套用智慧修整)
        self.update_tree(self.tree_low_stock, get_low_stock_materials(), [0, 1, 2, 3])
        self.update_tree(self.tree_exp_mat, get_expiring_raw_materials(), [2, 0, 1])
        
        tops = get_top_selling_products(limit=3)
        self.update_tree_custom(self.tree_top3, tops)
        
        self.update_tree(self.tree_exp_prod, get_expiring_products(), [2, 0, 1])

    # ⚠️ 智慧修整小幫手
    def smart_format(self, value):
        try:
            f = float(value)
            if f.is_integer(): return int(f)
            return round(f, 2)
        except:
            return value

    def update_tree(self, tree, data, indices):
        for item in tree.get_children(): tree.delete(item)
        if not data: return
        for i, row in enumerate(data):
            # 針對每一欄都嘗試修整
            vals = [self.smart_format(row[idx]) for idx in indices]
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.insert("", "end", values=vals, tags=(tag,))

    def update_tree_custom(self, tree, data):
        for item in tree.get_children(): tree.delete(item)
        for i, row in enumerate(data):
            tag = 'even' if i % 2 == 0 else 'odd'
            # Top 3: 排名, 名稱, 銷量(修整)
            qty = self.smart_format(row[1])
            tree.insert("", "end", values=(f"No.{i+1}", row[0], qty), tags=(tag,))