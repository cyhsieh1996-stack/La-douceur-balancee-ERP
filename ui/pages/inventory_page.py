import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font, Layout
from logic.inventory_logic import add_inventory_adjustment, get_adjustment_history, get_material_current_stock
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category, get_all_materials
from logic.products_logic import get_all_products

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.tabview = ctk.CTkTabview(self, width=400)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("庫存現況")
        self.tabview.add("消耗/盤點作業")

        # Tab 1
        self.tab_overview = self.tabview.tab("庫存現況")
        self.tab_overview.columnconfigure(0, weight=1); self.tab_overview.columnconfigure(1, weight=1); self.tab_overview.rowconfigure(0, weight=1)
        self.frame_mat_stock = ctk.CTkFrame(self.tab_overview, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.frame_mat_stock.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        self.create_material_stock_view(self.frame_mat_stock)
        self.frame_prod_stock = ctk.CTkFrame(self.tab_overview, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.frame_prod_stock.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        self.create_product_stock_view(self.frame_prod_stock)

        # Tab 2
        self.tab_ops = self.tabview.tab("消耗/盤點作業")
        self.form_card = ctk.CTkFrame(self.tab_ops, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 15))
        self.create_form(self.form_card)

        self.table_card = ctk.CTkFrame(self.tab_ops, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table(self.table_card)
        
        self.refresh_data()

    def create_material_stock_view(self, parent):
        ctk.CTkLabel(parent, text="📦 原料庫存", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(pady=(15, 10))
        cols = ("name", "stock", "unit", "safe"); headers = ["原料名稱", "庫存", "單位", "安全量"]; widths = [150, 80, 50, 80]
        style = ttk.Style()
        self.tree_mat = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths): self.tree_mat.heading(c, text=h); self.tree_mat.column(c, width=w, anchor="center")
        self.tree_mat.tag_configure('low', foreground=Color.DANGER); self.tree_mat.tag_configure('even', background=Color.TABLE_ROW_ALT); self.tree_mat.tag_configure('odd', background='white')
        self.tree_mat.pack(fill="both", expand=True, padx=10, pady=10)

    def create_product_stock_view(self, parent):
        ctk.CTkLabel(parent, text="🎂 產品庫存", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(pady=(15, 10))
        cols = ("name", "stock", "price"); headers = ["產品名稱", "庫存", "售價"]; widths = [180, 80, 80]
        self.tree_prod = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths): self.tree_prod.heading(c, text=h); self.tree_prod.column(c, width=w, anchor="center")
        self.tree_prod.tag_configure('zero', foreground=Color.TEXT_LIGHT); self.tree_prod.tag_configure('even', background=Color.TABLE_ROW_ALT); self.tree_prod.tag_configure('odd', background='white')
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)

    def create_form(self, parent):
        ctk.CTkLabel(parent, text="原料消耗 / 盤點作業", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(Layout.CARD_PADDING, 10))
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, Layout.CARD_PADDING))
        content.columnconfigure((0, 1, 2, 3), weight=1) # 4欄
        
        def create_field(parent, label, r, c): 
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=r, column=c, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if c == 3: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            e = ctk.CTkEntry(f, height=35); e.pack(fill="x")
            return e
        
        def create_combo(parent, label, r, c): 
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=r, column=c, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if c == 3: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            cb = ctk.CTkComboBox(f, height=35, state="readonly"); cb.pack(fill="x")
            return cb

        # Row 0
        self.combo_category = create_combo(content, "類別", 0, 0); self.combo_category.configure(command=self.on_category_change)
        self.combo_material = create_combo(content, "原料", 0, 1); self.combo_material.configure(command=self.on_material_selected)
        
        # 庫存顯示 (包裝一下讓它對齊)
        stock_f = ctk.CTkFrame(content, fg_color="transparent")
        stock_f.grid(row=0, column=2, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
        ctk.CTkLabel(stock_f, text=" ", font=Font.BODY).pack(anchor="w", pady=(0, 5)) # 佔位用
        self.lbl_current_stock = ctk.CTkLabel(stock_f, text="目前庫存: --", text_color=Color.INFO, font=("Arial", 16, "bold"))
        self.lbl_current_stock.pack(anchor="w", pady=5)

        self.combo_action = create_combo(content, "動作類型", 0, 3)
        self.combo_action.configure(values=["領用/消耗 (-)", "盤點盤虧 (-)", "報廢 (-)", "盤點盤盈 (+)", "其他增加 (+)"])
        self.combo_action.set("領用/消耗 (-)")

        # Row 1
        self.entry_qty = create_field(content, "異動數量", 1, 0)
        
        # 備註跨兩欄
        note_f = ctk.CTkFrame(content, fg_color="transparent")
        note_f.grid(row=1, column=1, columnspan=2, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
        ctk.CTkLabel(note_f, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
        self.entry_note = ctk.CTkEntry(note_f, height=35); self.entry_note.pack(fill="x")

        # 按鈕 (Row 2)
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=4, pady=(10, 0), sticky="e")
        self.btn_submit = ctk.CTkButton(btn_row, text="確認調整", fg_color=Color.PRIMARY, width=140, height=38, command=self.handle_submit)
        self.btn_submit.pack(side="right")

    def create_table(self, parent):
        cols = ("date", "name", "action", "qty", "unit", "note"); headers = ["時間", "原料名稱", "動作", "變動量", "單位", "備註"]; widths = [150, 150, 120, 80, 60, 200]
        self.tree = ttk.Treeview(parent, columns=cols, show="headings")
        for c, h, w in zip(cols, headers, widths): self.tree.heading(c, text=h); self.tree.column(c, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT); self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        # 1. 更新 Tab 1 原料列表 (使用數字索引)
        for i in self.tree_mat.get_children(): self.tree_mat.delete(i)
        mats = get_all_materials()
        for i, row in enumerate(mats): 
            stock = row[7]; safe = row[8]
            tag_row = 'even' if i % 2 == 0 else 'odd'
            tag_alert = 'low' if stock < safe else ''
            self.tree_mat.insert("", "end", values=(row[1], stock, row[5], safe), tags=(tag_row, tag_alert))

        # 2. 更新 Tab 1 產品列表 (使用數字索引)
        for i in self.tree_prod.get_children(): self.tree_prod.delete(i)
        prods = get_all_products()
        for i, row in enumerate(prods):
            stock = int(row[6])
            tag_row = 'even' if i % 2 == 0 else 'odd'
            tag_alert = 'zero' if stock <= 0 else ''
            self.tree_prod.insert("", "end", values=(row[1], stock, int(row[3])), tags=(tag_row, tag_alert))

        # 3. 更新 Tab 2
        cats = get_existing_categories()
        if cats: self.combo_category.configure(values=cats); self.combo_category.set("請選擇")
        else: self.combo_category.set("無分類資料")
        
        # 4. 更新調整紀錄 (使用數字索引)
        for i in self.tree.get_children(): self.tree.delete(i)
        logs = get_adjustment_history()
        for i, row in enumerate(logs):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5]), tags=(tag,))

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