import customtkinter as ctk
from tkinter import ttk
from ui.theme import Color, Font
from logic.dashboard_logic import (
    get_low_stock_materials, 
    get_expiring_products, 
    get_expiring_raw_materials,
    get_top_selling_products,
    get_weekly_finance,
    get_dashboard_summary
)

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 標題
        title = ctk.CTkLabel(self, text="戰情中心 Dashboard", font=Font.TITLE, text_color=Color.TEXT_DARK)
        title.pack(anchor="w", pady=(0, 10))

        # === 頂部統計列 ===
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 10))
        self.stats_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.lbl_revenue = self.create_stat_card(self.stats_frame, "💰 本週營業額", "$0", 0, "#27AE60") # 綠
        self.lbl_cost = self.create_stat_card(self.stats_frame, "💸 本週成本", "$0", 1, "#C0392B")    # 紅
        self.lbl_profit = self.create_stat_card(self.stats_frame, "📈 本週淨利", "$0", 2, "#2980B9")  # 藍
        self.lbl_mat_cnt = self.create_stat_card(self.stats_frame, "📦 原料總數", "0", 3, Color.TEXT_DARK)
        self.lbl_prod_cnt = self.create_stat_card(self.stats_frame, "🍰 產品總數", "0", 4, Color.TEXT_DARK)

        # === 下方內容區 (三欄式) ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.columnconfigure((0, 1, 2), weight=1)

        # 左欄：原料警報
        self.create_left_panel(self.content_frame)
        
        # 中欄：熱銷排行
        self.create_center_panel(self.content_frame)
        
        # 右欄：成品效期
        self.create_right_panel(self.content_frame)

        self.refresh_dashboard()

    def create_stat_card(self, parent, title, value, col, color):
        card = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        card.grid(row=0, column=col, padx=5, sticky="ew")
        ctk.CTkLabel(card, text=title, font=Font.BODY, text_color=Color.TEXT_LIGHT).pack(pady=(10, 0))
        lbl = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color=color)
        lbl.pack(pady=(0, 10))
        return lbl

    def create_left_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, padx=5, sticky="nsew")
        
        # 1. 缺貨原料
        self.create_table_card(frame, "🚨 原料缺貨警報", 
                               ["名稱", "目前", "安全"], [100, 50, 50], 
                               "tree_low_stock", "#FFEBEE")
        
        # 2. 原料過期
        self.create_table_card(frame, "⚠️ 原料即將過期 (30天內)", 
                               ["效期", "名稱", "批號"], [80, 100, 80], 
                               "tree_exp_mat", "#FFF3E0")

    def create_center_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=1, padx=5, sticky="nsew")
        
        # 熱銷排行
        self.create_table_card(frame, "🏆 本週熱銷 Top 3", 
                               ["排名", "產品名稱", "銷量"], [50, 150, 60], 
                               "tree_top3", "#E8F8F5")

    def create_right_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=2, padx=5, sticky="nsew")
        
        # 成品過期
        self.create_table_card(frame, "⏳ 成品即將過期 (7天內)", 
                               ["效期", "產品", "批號"], [80, 100, 100], 
                               "tree_exp_prod", "#FFF8E1")

    def create_table_card(self, parent, title, headers, widths, attr_name, bg_color):
        card = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        card.pack(fill="x", pady=(0, 15))
        
        header = ctk.CTkFrame(card, fg_color=bg_color, corner_radius=10, height=30)
        header.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(header, text=title, font=Font.SMALL, text_color=Color.TEXT_DARK).pack(pady=5)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", rowheight=25, font=("Arial", 11))
        
        tree = ttk.Treeview(card, columns=headers, show="headings", height=6)
        for col, w in zip(headers, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="x", padx=5, pady=5)
        
        setattr(self, attr_name, tree)

    def refresh_dashboard(self):
        # 1. 財務
        fin = get_weekly_finance()
        self.lbl_revenue.configure(text=f"${fin['revenue']:,}")
        self.lbl_cost.configure(text=f"${fin['cost']:,}")
        self.lbl_profit.configure(text=f"${fin['profit']:,}")
        
        # 2. 總數
        summ = get_dashboard_summary()
        self.lbl_mat_cnt.configure(text=str(summ['material_count']))
        self.lbl_prod_cnt.configure(text=str(summ['product_count']))
        
        # 3. 缺貨
        self.update_tree(self.tree_low_stock, get_low_stock_materials(), [0, 1, 2])
        
        # 4. 原料過期
        self.update_tree(self.tree_exp_mat, get_expiring_raw_materials(), [2, 0, 1])
        
        # 5. 熱銷
        tops = get_top_selling_products()
        for item in self.tree_top3.get_children(): self.tree_top3.delete(item)
        for i, row in enumerate(tops):
            self.tree_top3.insert("", "end", values=(f"No.{i+1}", row[0], int(row[1])))
            
        # 6. 成品過期
        self.update_tree(self.tree_exp_prod, get_expiring_products(), [2, 0, 1])

    def update_tree(self, tree, data, indices):
        for item in tree.get_children(): tree.delete(item)
        for row in data:
            vals = [row[i] for i in indices]
            tree.insert("", "end", values=vals)