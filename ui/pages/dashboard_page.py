import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from ui.theme import Color, Font
from logic.dashboard_logic import (
    get_low_stock_materials, get_expiring_products, get_expiring_raw_materials,
    get_top_selling_products,
    get_recent_production, get_recent_inbound
)
from logic.export_logic import export_all_data

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # --- 標題區 (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 標題
        ctk.CTkLabel(header_frame, text="戰情中心 Dashboard", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(side="left")
        
        # 匯出按鈕
        btn_export = ctk.CTkButton(header_frame, text="📥 匯出資料備份", fg_color=Color.INFO, width=120, height=36, command=self.handle_export)
        btn_export.pack(side="right")

        # ⚠️ 變更：移除了上方的 stats_frame (卡片區)

        # --- 六宮格表格區 ---
        # 因為移除了上方卡片，這裡的空間變大了，我們可以讓表格更長
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self.content_frame.columnconfigure((0, 1, 2), weight=1)
        self.content_frame.rowconfigure((0, 1), weight=1)

        # 🚀 第一排 (Top Row)
        # 1-1: 熱銷 (改為 Top 10)
        self.create_table_section(self.content_frame, "🏆 熱銷產品排行", ["排名", "產品名稱", "銷量"], [50, 160, 70], 0, 0, "tree_top3")
        # 1-2: 最近入庫
        self.create_table_section(self.content_frame, "📥 最近入庫紀錄", ["時間", "原料", "數量", "單位"], [100, 120, 60, 50], 0, 1, "tree_rec_inbound")
        # 1-3: 原料過期
        self.create_table_section(self.content_frame, "⚠️ 原料即將過期", ["效期", "名稱", "批號"], [90, 110, 80], 0, 2, "tree_exp_mat")

        # 🚀 第二排 (Bottom Row)
        # 2-1: 原料缺貨
        self.create_table_section(self.content_frame, "🚨 原料缺貨警報", ["名稱", "目前", "安全", "單位"], [100, 60, 60, 50], 1, 0, "tree_low_stock")
        # 2-2: 最近生產
        self.create_table_section(self.content_frame, "👩‍🍳 最近生產紀錄", ["時間", "產品", "數量", "批號"], [100, 120, 60, 80], 1, 1, "tree_rec_prod")
        # 2-3: 成品過期
        self.create_table_section(self.content_frame, "⏳ 成品即將過期", ["效期", "產品", "批號"], [90, 120, 90], 1, 2, "tree_exp_prod")

        self.refresh_dashboard()

    def handle_export(self):
        folder = filedialog.askdirectory(title="選擇匯出儲存位置")
        if not folder: return
        success, msg = export_all_data(folder)
        if success: messagebox.showinfo("成功", msg)
        else: messagebox.showerror("失敗", msg)

    def create_table_section(self, parent, title, headers, widths, row, col, attr_name):
        container = ctk.CTkFrame(parent, fg_color=Color.WHITE_CARD, corner_radius=8)
        container.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # 標題
        header_box = ctk.CTkFrame(container, fg_color="transparent", height=40)
        header_box.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(header_box, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(side="left")
        
        # 表格區
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
        
        # ⚠️ 優化：增加高度至 11 行 (利用原本卡片的空間)
        tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=11)
        
        for col_name, w in zip(headers, widths):
            tree.heading(col_name, text=col_name)
            tree.column(col_name, width=w, minwidth=40, anchor="center", stretch=True)
        
        tree.tag_configure('odd', background='white')
        tree.tag_configure('even', background="#F9FAFB")
        
        tree.pack(side="left", fill="both", expand=True, padx=5)
        setattr(self, attr_name, tree)

    def refresh_dashboard(self):
        # ⚠️ 更新：不需要再載入 get_monthly_finance 或 dashboard_summary 了
        
        self.update_tree(self.tree_low_stock, get_low_stock_materials(), [0, 1, 2, 3])
        
        # ⚠️ 優化：抓取 Top 12，填滿長表格
        tops = get_top_selling_products(limit=12)
        self.update_tree_custom(self.tree_top3, tops)
        
        self.update_tree(self.tree_exp_prod, get_expiring_products(), [2, 0, 1])
        self.update_tree(self.tree_exp_mat, get_expiring_raw_materials(), [2, 0, 1])
        
        # ⚠️ 優化：抓取最近 12 筆紀錄
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
                # 日期截斷
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