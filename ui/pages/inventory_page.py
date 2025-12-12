import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font, Layout
from logic.inventory_logic import add_inventory_adjustment, get_adjustment_history, get_material_current_stock
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 20))
        self.create_form()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="原料消耗 / 盤點作業", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2, 3), weight=1) # 4欄對齊
        
        def add_field(label_text, row, col):
            ctk.CTkLabel(content, text=label_text, font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=row*2, column=col, padx=Layout.GRID_PADX, pady=(5, 0), sticky="w")

        # 第一排
        add_field("類別", 0, 0); self.combo_category = ctk.CTkComboBox(content, state="readonly", command=self.on_category_change)
        self.combo_category.set("請選擇"); self.combo_category.grid(row=1, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        add_field("原料", 0, 1); self.combo_material = ctk.CTkComboBox(content, state="readonly", command=self.on_material_selected)
        self.combo_material.set("請先選類別"); self.combo_material.grid(row=1, column=1, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        # 目前庫存顯示在原料旁邊的下方，或者獨立一格
        self.lbl_current_stock = ctk.CTkLabel(content, text="目前庫存: --", text_color=Color.INFO, font=("Arial", 14, "bold"))
        self.lbl_current_stock.grid(row=1, column=2, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="w")
        
        add_field("動作類型", 0, 3); self.combo_action = ctk.CTkComboBox(content, state="readonly", values=["領用/消耗 (-)", "盤點盤虧 (-)", "報廢 (-)", "盤點盤盈 (+)", "其他增加 (+)"])
        self.combo_action.set("領用/消耗 (-)"); self.combo_action.grid(row=1, column=3, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        # 第二排
        add_field("異動數量", 1, 0); self.entry_qty = ctk.CTkEntry(content, placeholder_text="輸入數字")
        self.entry_qty.grid(row=3, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        add_field("備註", 1, 1); self.entry_note = ctk.CTkEntry(content, placeholder_text="說明原因")
        self.entry_note.grid(row=3, column=1, columnspan=2, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        # 按鈕
        self.btn_submit = ctk.CTkButton(content, text="確認調整", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_submit)
        self.btn_submit.grid(row=3, column=3, padx=Layout.GRID_PADX, pady=(10, 20), sticky="e")

    def create_table(self):
        # ... (表格部分與前面類似，重點是加入斑馬紋) ...
        columns = ("date", "name", "action", "qty", "unit", "note")
        headers = ["時間", "原料名稱", "動作", "變動量", "單位", "備註"]
        widths = [150, 150, 120, 80, 60, 200]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h); self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5); self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        cats = get_existing_categories()
        if cats: self.combo_category.configure(values=cats); self.combo_category.set("請選擇")
        else: self.combo_category.set("無分類資料")
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_adjustment_history()
        for i, row in enumerate(rows):
            values = (row['date'], row['name'], row['action_type'], row['change_qty'], row['unit'], row['note'])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    # ... (其餘邏輯保持不變) ...
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