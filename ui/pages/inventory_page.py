import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font, Layout
from logic.inventory_logic import add_inventory_adjustment, get_adjustment_history, get_material_current_stock
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category, get_all_materials
from logic.products_logic import get_all_products

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 建立 Tab View
        self.tabview = ctk.CTkTabview(self, width=400)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("庫存現況")
        self.tabview.add("消耗/盤點作業")

        # === Tab 1: 庫存現況 (左原料、右產品) ===
        self.tab_overview = self.tabview.tab("庫存現況")
        self.tab_overview.columnconfigure(0, weight=1)
        self.tab_overview.columnconfigure(1, weight=1)
        self.tab_overview.rowconfigure(0, weight=1)

        # 1-1. 原料庫存區 (左)
        self.frame_mat_stock = ctk.CTkFrame(self.tab_overview, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.frame_mat_stock.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        self.create_material_stock_view(self.frame_mat_stock)

        # 1-2. 產品庫存區 (右)
        self.frame_prod_stock = ctk.CTkFrame(self.tab_overview, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.frame_prod_stock.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        self.create_product_stock_view(self.frame_prod_stock)

        # === Tab 2: 消耗/盤點 (原功能) ===
        self.tab_ops = self.tabview.tab("消耗/盤點作業")
        
        self.form_card = ctk.CTkFrame(self.tab_ops, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 20))
        self.create_form(self.form_card)

        self.table_card = ctk.CTkFrame(self.tab_ops, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table(self.table_card)
        
        self.refresh_data()

    # --- Tab 1: 庫存總覽功能 ---
    def create_material_stock_view(self, parent):
        ctk.CTkLabel(parent, text="📦 原料庫存", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(pady=(15, 10))
        
        cols = ("name", "stock", "unit", "safe")
        headers = ["原料名稱", "庫存", "單位", "安全量"]
        widths = [150, 80, 50, 80]
        
        self.tree_mat = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths):
            self.tree_mat.heading(c, text=h)
            self.tree_mat.column(c, width=w, anchor="center")
        
        self.tree_mat.tag_configure('low', foreground=Color.DANGER)
        self.tree_mat.tag_configure('even', background=Color.TABLE_ROW_ALT)
        self.tree_mat.tag_configure('odd', background='white')
        
        self.tree_mat.pack(fill="both", expand=True, padx=10, pady=10)

    def create_product_stock_view(self, parent):
        ctk.CTkLabel(parent, text="🎂 產品庫存", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(pady=(15, 10))
        
        cols = ("name", "stock", "price")
        headers = ["產品名稱", "庫存", "售價"]
        widths = [180, 80, 80]
        
        self.tree_prod = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths):
            self.tree_prod.heading(c, text=h)
            self.tree_prod.column(c, width=w, anchor="center")
            
        self.tree_prod.tag_configure('zero', foreground=Color.TEXT_LIGHT)
        self.tree_prod.tag_configure('even', background=Color.TABLE_ROW_ALT)
        self.tree_prod.tag_configure('odd', background='white')

        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Tab 2: 消耗/盤點功能 ---
    def create_form(self, parent):
        ctk.CTkLabel(parent, text="原料消耗 / 盤點作業", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2, 3), weight=1)
        
        def add_field(label, r, c): ctk.CTkLabel(content, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=r*2, column=c, padx=Layout.GRID_PADX, pady=(5, 0), sticky="w")

        add_field("類別", 0, 0); self.combo_category = ctk.CTkComboBox(content, state="readonly", command=self.on_category_change); self.combo_category.set("請選擇"); self.combo_category.grid(row=1, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        add_field("原料", 0, 1); self.combo_material = ctk.CTkComboBox(content, state="readonly", command=self.on_material_selected); self.combo_material.set("請先選類別"); self.combo_material.grid(row=1, column=1, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        self.lbl_current_stock = ctk.CTkLabel(content, text="目前庫存: --", text_color=Color.INFO, font=("Arial", 14, "bold")); self.lbl_current_stock.grid(row=1, column=2, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="w")
        add_field("動作類型", 0, 3); self.combo_action = ctk.CTkComboBox(content, state="readonly", values=["領用/消耗 (-)", "盤點盤虧 (-)", "報廢 (-)", "盤點盤盈 (+)", "其他增加 (+)"]); self.combo_action.set("領用/消耗 (-)"); self.combo_action.grid(row=1, column=3, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        add_field("異動數量", 1, 0); self.entry_qty = ctk.CTkEntry(content, placeholder_text="輸入數字"); self.entry_qty.grid(row=3, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        add_field("備註", 1, 1); self.entry_note = ctk.CTkEntry(content, placeholder_text="說明原因"); self.entry_note.grid(row=3, column=1, columnspan=2, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        self.btn_submit = ctk.CTkButton(content, text="確認調整", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_submit); self.btn_submit.grid(row=3, column=3, padx=Layout.GRID_PADX, pady=(10, 20), sticky="e")

    def create_table(self, parent):
        cols = ("date", "name", "action", "qty", "unit", "note")
        headers = ["時間", "原料名稱", "動作", "變動量", "單位", "備註"]
        widths = [150, 150, 120, 80, 60, 200]
        self.tree = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths): self.tree.heading(c, text=h); self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_data(self):
        # 1. 更新 Tab 1 原料列表
        for i in self.tree_mat.get_children(): self.tree_mat.delete(i)
        mats = get_all_materials()
        for i, row in enumerate(mats): 
            stock = row[7]; safe = row[8]
            tag_row = 'even' if i % 2 == 0 else 'odd'
            tag_alert = 'low' if stock < safe else ''
            self.tree_mat.insert("", "end", values=(row[1], stock, row[5], safe), tags=(tag_row, tag_alert))

        # 2. 更新 Tab 1 產品列表
        for i in self.tree_prod.get_children(): self.tree_prod.delete(i)
        prods = get_all_products()
        for i, row in enumerate(prods):
            stock = int(row[6])
            tag_row = 'even' if i % 2 == 0 else 'odd'
            tag_alert = 'zero' if stock <= 0 else ''
            self.tree_prod.insert("", "end", values=(row[1], stock, int(row[3])), tags=(tag_row, tag_alert))

        # 3. 更新 Tab 2 操作區
        cats = get_existing_categories()
        if cats: self.combo_category.configure(values=cats); self.combo_category.set("請選擇")
        else: self.combo_category.set("無分類資料")
        
        # 4. 更新 Tab 2 歷史紀錄
        for i in self.tree.get_children(): self.tree.delete(i)
        logs = get_adjustment_history()
        for i, row in enumerate(logs):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(row['date'], row['name'], row['action_type'], row['change_qty'], row['unit'], row['note']), tags=(tag,))

    def on_category_change(self, val):
        if not val or "請選擇" in val: return
        mats = get_materials_by_category(val)
        if mats: self.combo_material.configure(values=mats); self.combo_material.set(mats[0]); self.on_material_selected(mats[0])
        else: self.combo_material.configure(values=["無原料"]); self.combo_material.set("無原料"); self.lbl_current_stock.configure(text="目前庫存: --")
    
    def on_material_selected(self, val):
        if "無原料" in val: return
        try: mat_id = int(val.split(" - ")[0]); stock, unit = get_material_current_stock(mat_id); self.lbl_current_stock.configure(text=f"目前庫存: {stock} {unit}")
        except: self.lbl_current_stock.configure(text="目前庫存: --")
    
    def handle_submit(self):
        mat_str = self.combo_material.get(); action = self.combo_action.get(); qty_str = self.entry_qty.get(); note = self.entry_note.get()
        if "請先選" in mat_str or not mat_str: messagebox.showwarning("警告", "請選擇原料"); return
        if not qty_str: messagebox.showwarning("警告", "請輸入數量"); return
        try: mat_id = int(mat_str.split(" - ")[0]); qty = float(qty_str)
        except: messagebox.showerror("錯誤", "數量格式錯誤"); return
        final_qty = -abs(qty) if "(-)" in action else abs(qty)
        success, msg = add_inventory_adjustment(mat_id, final_qty, action, note)
        if success:
            messagebox.showinfo("成功", f"已更新庫存！\n變動: {final_qty}")
            self.entry_qty.delete(0, "end"); self.entry_note.delete(0, "end"); self.refresh_data(); self.on_material_selected(mat_str)
        else: messagebox.showerror("失敗", msg)