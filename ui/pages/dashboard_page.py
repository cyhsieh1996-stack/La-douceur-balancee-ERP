import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from ui.theme import Color, Font
from logic.dashboard_logic import (
    get_low_stock_materials, get_expiring_products, get_expiring_raw_materials,
    get_top_selling_products, get_weekly_finance, get_dashboard_summary
)
from logic.export_logic import export_all_data

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 標題與匯出按鈕區
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header_frame, text="戰情中心 Dashboard", font=Font.TITLE, text_color=Color.TEXT_DARK)
        title.pack(side="left")
        
        btn_export = ctk.CTkButton(header_frame, text="📥 匯出資料備份", 
                                   fg_color=Color.INFO, width=120, height=35,
                                   command=self.handle_export)
        btn_export.pack(side="right")

        # 頂部統計卡片
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 20))
        self.stats_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.lbl_revenue = self.create_stat_card(self.stats_frame, "本週營業額", "$0", 0)
        self.lbl_cost = self.create_stat_card(self.stats_frame, "本週成本", "$0", 1)
        self.lbl_profit = self.create_stat_card(self.stats_frame, "本週淨利", "$0", 2, value_color=Color.PRIMARY)
        self.lbl_mat_cnt = self.create_stat_card(self.stats_frame, "原料品項", "0", 3)
        self.lbl_prod_cnt = self.create_stat_card(self.stats_frame, "產品品項", "0", 4)

        # 下方資訊區
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
        ctk.CTkLabel(card, text=title, font=Font.SMALL, text_color=Color.TEXT_LIGHT).pack(pady=(15, 5))
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
        self.create_table_section(frame, "🏆 本週熱銷 Top 3", ["排名", "產品名稱", "銷量"], [60, 180, 80], "tree_top3")

    def create_right_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=2, padx=5, sticky="nsew")
        self.create_table_section(frame, "⏳ 成品即將過期", ["效期", "產品", "批號"], [100, 120, 100], "tree_exp_prod")

    def create_table_section(self, parent, title, headers, widths, attr_name):
        container = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        container.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(container, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(anchor="w", padx=15, pady=(15, 5))
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")
        
        tree = ttk.Treeview(container, columns=headers, show="headings", height=5)
        for col, w in zip(headers, widths):
            tree.heading(col, text=col); tree.column(col, width=w, anchor="center")
        
        # ⚠️ 斑馬紋
        tree.tag_configure('odd', background='white')
        tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        tree.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        setattr(self, attr_name, tree)

    def refresh_dashboard(self):
        fin = get_weekly_finance()
        self.lbl_revenue.configure(text=f"${fin['revenue']:,}")
        self.lbl_cost.configure(text=f"${fin['cost']:,}")
        self.lbl_profit.configure(text=f"${fin['profit']:,}")
        summ = get_dashboard_summary()
        self.lbl_mat_cnt.configure(text=f"{summ['material_count']}")
        self.lbl_prod_cnt.configure(text=f"{summ['product_count']}")
        self.update_tree(self.tree_low_stock, get_low_stock_materials(), [0, 1, 2, 3])
        self.update_tree(self.tree_exp_mat, get_expiring_raw_materials(), [2, 0, 1])
        tops = get_top_selling_products(limit=3)
        self.update_tree_custom(self.tree_top3, tops)
        self.update_tree(self.tree_exp_prod, get_expiring_products(), [2, 0, 1])

    def update_tree(self, tree, data, indices):
        for item in tree.get_children(): tree.delete(item)
        if not data: return
        for i, row in enumerate(data):
            vals = [row[i] for i in indices]
            # ⚠️ 應用斑馬紋
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.insert("", "end", values=vals, tags=(tag,))

    def update_tree_custom(self, tree, data):
        for item in tree.get_children(): tree.delete(item)
        for i, row in enumerate(data):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.insert("", "end", values=(f"No.{i+1}", row[0], int(row[1])), tags=(tag,))