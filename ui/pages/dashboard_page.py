import customtkinter as ctk
from tkinter import ttk
from ui.theme import Color, Font
from logic.dashboard_logic import get_low_stock_materials, get_expiring_batches, get_dashboard_summary

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="儀表板 Dashboard", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 20))

        # 2. 頂部概況卡片區 (使用 Grid 排列三個小卡片)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 20))
        self.stats_frame.columnconfigure((0, 1, 2), weight=1)
        
        self.card_1 = self.create_stat_card(self.stats_frame, "📦 原料品項數", "--", 0)
        self.card_2 = self.create_stat_card(self.stats_frame, "🍰 產品品項數", "--", 1)
        self.card_3 = self.create_stat_card(self.stats_frame, "🚨 缺貨原料", "--", 2, text_color=Color.DANGER)

        # 3. 下方兩大區塊 (左右分割)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="both", expand=True)
        self.bottom_frame.columnconfigure((0, 1), weight=1)

        # 左邊：缺貨警報
        self.create_low_stock_panel(self.bottom_frame, 0)
        
        # 右邊：效期警報
        self.create_expiry_panel(self.bottom_frame, 1)

        # 載入資料
        self.refresh_dashboard()

    def create_stat_card(self, parent, title, value, col_idx, text_color=Color.PRIMARY):
        """建立上方的小統計卡片"""
        card = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        card.grid(row=0, column=col_idx, padx=10, sticky="ew")
        
        lbl_title = ctk.CTkLabel(card, text=title, font=Font.BODY, text_color=Color.TEXT_LIGHT)
        lbl_title.pack(pady=(15, 0))
        
        lbl_val = ctk.CTkLabel(card, text=value, font=("Arial", 36, "bold"), text_color=text_color)
        lbl_val.pack(pady=(5, 15))
        
        return lbl_val # 回傳 value label 以便後續更新

    def create_low_stock_panel(self, parent, col_idx):
        """左側：缺貨清單"""
        frame = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="nsew")
        
        # 標題列
        header = ctk.CTkFrame(frame, fg_color="#FFEEEE", corner_radius=10) # 淡紅色背景
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="⚠️ 原料庫存不足 (需叫貨)", font=Font.SUBTITLE, text_color=Color.DANGER).pack(pady=10)

        # 表格
        columns = ("name", "stock", "safe", "unit", "vendor")
        headers = ["原料名稱", "目前", "安全", "單位", "廠商"]
        widths = [120, 60, 60, 50, 80]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", rowheight=30, font=Font.SMALL)
        
        self.tree_stock = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col, h, w in zip(columns, headers, widths):
            self.tree_stock.heading(col, text=h)
            self.tree_stock.column(col, width=w, anchor="center")
            
        self.tree_stock.pack(fill="both", expand=True, padx=10, pady=10)

    def create_expiry_panel(self, parent, col_idx):
        """右側：即將過期清單"""
        frame = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=10)
        frame.grid(row=0, column=col_idx, padx=10, pady=10, sticky="nsew")
        
        # 標題列
        header = ctk.CTkFrame(frame, fg_color="#FFF8E1", corner_radius=10) # 淡橘色背景
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="⏳ 即將過期批號 (7日內)", font=Font.SUBTITLE, text_color="#E67E22").pack(pady=10)

        # 表格
        columns = ("date", "batch", "name", "qty")
        headers = ["有效日期", "批號", "產品", "生產量"]
        widths = [100, 120, 120, 60]
        
        self.tree_expiry = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col, h, w in zip(columns, headers, widths):
            self.tree_expiry.heading(col, text=h)
            self.tree_expiry.column(col, width=w, anchor="center")
            
        self.tree_expiry.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_dashboard(self):
        # 1. 更新上方統計
        summary = get_dashboard_summary()
        self.card_1.configure(text=str(summary['material_count']))
        self.card_2.configure(text=str(summary['product_count']))
        self.card_3.configure(text=str(summary['low_stock_count']))
        
        # 2. 更新缺貨表格
        for item in self.tree_stock.get_children():
            self.tree_stock.delete(item)
        
        low_stocks = get_low_stock_materials()
        for row in low_stocks:
            # name, stock, safe_stock, unit, vendor
            self.tree_stock.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

        # 3. 更新過期表格
        for item in self.tree_expiry.get_children():
            self.tree_expiry.delete(item)
            
        expiring = get_expiring_batches()
        for row in expiring:
            # name, batch, expiry, qty (注意順序調整)
            # SQL回傳: name, batch, expiry, qty
            # 表格顯示: expiry, batch, name, qty
            self.tree_expiry.insert("", "end", values=(row[2], row[1], row[0], row[3]))