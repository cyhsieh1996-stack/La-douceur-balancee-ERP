import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font
from logic.inventory_logic import add_inventory_adjustment, get_adjustment_history, get_material_current_stock
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category

class InventoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 標題 (修改標題以符合新功能)
        title = ctk.CTkLabel(
            self, 
            text="庫存調整與紀錄 Inventory Log", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 操作區 (白色卡片)
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))
        self.create_form()

        # 3. 歷史紀錄 (白色卡片)
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        self.form_card.columnconfigure((0, 1, 2, 3), weight=1)
        
        # === 第一排 ===
        # 1. 類別
        ctk.CTkLabel(self.form_card, text="1. 類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.combo_category = ctk.CTkComboBox(self.form_card, state="readonly", command=self.on_category_change)
        self.combo_category.set("請選擇")
        self.combo_category.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. 原料
        ctk.CTkLabel(self.form_card, text="2. 原料", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.combo_material = ctk.CTkComboBox(self.form_card, state="readonly", command=self.on_material_selected)
        self.combo_material.set("請先選類別")
        self.combo_material.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="ew")

        # 3. 顯示目前庫存 (Label)
        self.lbl_current_stock = ctk.CTkLabel(self.form_card, text="目前庫存: --", text_color=Color.PRIMARY, font=("Arial", 14, "bold"))
        self.lbl_current_stock.grid(row=0, column=2, padx=20, pady=(20, 5), sticky="w")
        
        # 4. 動作類型
        ctk.CTkLabel(self.form_card, text="動作類型", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=3, padx=20, pady=(20, 5), sticky="w")
        self.combo_action = ctk.CTkComboBox(
            self.form_card, 
            state="readonly",
            values=["領用/消耗 (-)", "盤點盤虧 (-)", "報廢 (-)", "盤點盤盈 (+)", "其他增加 (+)"]
        )
        self.combo_action.set("領用/消耗 (-)")
        self.combo_action.grid(row=1, column=3, padx=20, pady=(0, 10), sticky="ew")

        # === 第二排 ===
        # 5. 數量
        ctk.CTkLabel(self.form_card, text="變動數量 (請輸入正數)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_qty = ctk.CTkEntry(self.form_card, placeholder_text="例如: 1")
        self.entry_qty.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # 6. 備註
        ctk.CTkLabel(self.form_card, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        self.entry_note = ctk.CTkEntry(self.form_card, placeholder_text="說明原因")
        self.entry_note.grid(row=3, column=1, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        # 7. 按鈕
        self.btn_submit = ctk.CTkButton(
            self.form_card, 
            text="確認調整", 
            fg_color=Color.PRIMARY, 
            hover_color=Color.PRIMARY_HOVER,
            font=Font.BODY,
            height=40,
            command=self.handle_submit
        )
        self.btn_submit.grid(row=3, column=3, padx=20, pady=(0, 20), sticky="ew")

    def create_table(self):
        title_label = ctk.CTkLabel(self.table_card, text="最近異動紀錄", font=Font.SUBTITLE, text_color=Color.TEXT_LIGHT)
        title_label.pack(anchor="w", padx=20, pady=(15, 10))

        columns = ("date", "name", "action", "qty", "unit", "note")
        headers = ["時間", "原料名稱", "動作", "變動量", "單位", "備註"]
        widths = [150, 150, 120, 80, 60, 200]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, fieldbackground="white", font=Font.SMALL)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        # 載入類別
        cats = get_existing_categories()
        if cats:
            self.combo_category.configure(values=cats)
            self.combo_category.set("請選擇")
        else:
            self.combo_category.set("無分類資料")
        
        # 載入歷史紀錄
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = get_adjustment_history()
        for row in rows:
            values = (row['date'], row['name'], row['action_type'], row['change_qty'], row['unit'], row['note'])
            self.tree.insert("", "end", values=values)

    def on_category_change(self, val):
        if not val or "請選擇" in val: return
        mats = get_materials_by_category(val)
        if mats:
            self.combo_material.configure(values=mats)
            self.combo_material.set(mats[0])
            self.on_material_selected(mats[0])
        else:
            self.combo_material.configure(values=["無原料"])
            self.combo_material.set("無原料")
            self.lbl_current_stock.configure(text="目前庫存: --")

    def on_material_selected(self, val):
        if "無原料" in val: return
        try:
            mat_id = int(val.split(" - ")[0])
            stock, unit = get_material_current_stock(mat_id)
            self.lbl_current_stock.configure(text=f"目前庫存: {stock} {unit}")
        except:
            self.lbl_current_stock.configure(text="目前庫存: --")

    def handle_submit(self):
        mat_str = self.combo_material.get()
        action = self.combo_action.get()
        qty_str = self.entry_qty.get()
        note = self.entry_note.get()

        if "請先選" in mat_str or not mat_str:
            messagebox.showwarning("警告", "請選擇原料")
            return
        if not qty_str:
            messagebox.showwarning("警告", "請輸入數量")
            return

        try:
            mat_id = int(mat_str.split(" - ")[0])
            qty = float(qty_str)
        except:
            messagebox.showerror("錯誤", "數量格式錯誤")
            return

        # 自動判斷正負號
        final_qty = qty
        if "(-)" in action:
            final_qty = -abs(qty)
        else:
            final_qty = abs(qty)

        success, msg = add_inventory_adjustment(mat_id, final_qty, action, note)
        
        if success:
            messagebox.showinfo("成功", f"已更新庫存！\n變動: {final_qty}")
            self.entry_qty.delete(0, "end")
            self.entry_note.delete(0, "end")
            self.refresh_data()
            self.on_material_selected(mat_str)
        else:
            messagebox.showerror("失敗", msg)