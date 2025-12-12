import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font
from logic.inbound_logic import add_inbound_record, get_inbound_history
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category

class InboundPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="原料入庫 Inbound", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 入庫操作區
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))

        self.create_form()

        # 3. 歷史紀錄區
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)

        self.create_table()
        
        # 4. 初始載入
        self.refresh_data()

    def create_form(self):
        self.form_card.columnconfigure((0, 1, 2), weight=1)
        
        # === 第一排 ===
        # 1. 類別
        ctk.CTkLabel(self.form_card, text="1. 類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.combo_category = ctk.CTkComboBox(self.form_card, state="readonly", command=self.on_category_change)
        self.combo_category.set("請選擇")
        self.combo_category.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. 品項
        ctk.CTkLabel(self.form_card, text="2. 品項", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.combo_material = ctk.CTkComboBox(self.form_card, state="readonly")
        self.combo_material.set("請先選擇類別")
        self.combo_material.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="ew")

        # 3. 數量
        ctk.CTkLabel(self.form_card, text="入庫數量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=20, pady=(20, 5), sticky="w")
        self.entry_qty = ctk.CTkEntry(self.form_card, placeholder_text="輸入數字")
        self.entry_qty.grid(row=1, column=2, padx=20, pady=(0, 10), sticky="ew")

        # === 第二排 ===
        # 4. 批號 (Batch)
        ctk.CTkLabel(self.form_card, text="批號", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_batch = ctk.CTkEntry(self.form_card, placeholder_text="例如：B20251212")
        self.entry_batch.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # 5. 效期 (Expiry)
        ctk.CTkLabel(self.form_card, text="有效期限", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.entry_expiry = ctk.CTkEntry(self.form_card, placeholder_text="YYYY-MM-DD")
        self.entry_expiry.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")

        # 6. 備註
        ctk.CTkLabel(self.form_card, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=2, padx=20, pady=(10, 5), sticky="w")
        self.entry_note = ctk.CTkEntry(self.form_card, placeholder_text="選填")
        self.entry_note.grid(row=3, column=2, padx=20, pady=(0, 20), sticky="ew")

        # === 按鈕 ===
        self.btn_submit = ctk.CTkButton(
            self.form_card, 
            text="確認入庫", 
            fg_color=Color.PRIMARY, 
            hover_color=Color.PRIMARY_HOVER,
            font=Font.BODY,
            height=40,
            command=self.handle_submit
        )
        self.btn_submit.grid(row=4, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")

    def create_table(self):
        title_label = ctk.CTkLabel(self.table_card, text="最近入庫紀錄", font=Font.SUBTITLE, text_color=Color.TEXT_LIGHT)
        title_label.pack(anchor="w", padx=20, pady=(15, 10))

        # 新增顯示 批號、效期
        columns = ("date", "name", "brand", "qty", "unit", "batch", "expiry", "note")
        headers = ["入庫時間", "原料名稱", "廠牌", "數量", "單位", "批號", "有效期限", "備註"]
        widths = [140, 140, 100, 60, 50, 100, 100, 150]

        # 設定 Treeview 樣式 (放大版)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", 
            background="white", 
            foreground=Color.TEXT_DARK,
            rowheight=35,               # 修改：行高從 30 改為 35 或 40
            fieldbackground="white",
            font=Font.SMALL             # 修改：使用 theme 裡面的變大字體
        )
        style.configure(
            "Treeview.Heading", 
            font=Font.TABLE_HEADER,     # 修改：使用 theme 裡面的表頭字體
            background="#F0F0F0",
            foreground=Color.TEXT_DARK
        )
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings", height=15)
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        categories = get_existing_categories()
        if categories:
            self.combo_category.configure(values=categories)
            self.combo_category.set("請選擇類別")
        else:
            self.combo_category.configure(values=["無資料"])
            self.combo_category.set("無資料")
            
        self.combo_material.set("")
        self.combo_material.configure(values=[])

        # 更新表格
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        rows = get_inbound_history()
        for row in rows:
            # 對應 Logic 回傳的順序
            values = (row['date'], row['name'], row['brand'], row['qty'], row['unit'], row['batch_number'], row['expiry_date'], row['note'])
            self.tree.insert("", "end", values=values)

    def on_category_change(self, selected_category):
        if not selected_category or selected_category == "請選擇類別":
            return
        materials = get_materials_by_category(selected_category)
        if materials:
            self.combo_material.configure(values=materials)
            self.combo_material.set(materials[0])
        else:
            self.combo_material.configure(values=["此類別無原料"])
            self.combo_material.set("此類別無原料")

    def handle_submit(self):
        selected_str = self.combo_material.get()
        qty_str = self.entry_qty.get()
        batch = self.entry_batch.get()
        expiry = self.entry_expiry.get()
        note = self.entry_note.get()

        if not selected_str or "無原料" in selected_str or "請先選擇" in selected_str:
            messagebox.showwarning("警告", "請選擇有效的原料")
            return

        if not qty_str:
            messagebox.showwarning("警告", "請輸入數量")
            return

        if not expiry:
            messagebox.showwarning("警告", "請輸入有效期限 (供日後警示用)")
            return

        try:
            material_id = int(selected_str.split(" - ")[0])
            qty = float(qty_str)
        except:
            messagebox.showerror("錯誤", "數量格式錯誤")
            return

        success, msg = add_inbound_record(material_id, qty, batch, expiry, note)

        if success:
            self.entry_qty.delete(0, "end")
            self.entry_batch.delete(0, "end")
            self.entry_expiry.delete(0, "end")
            self.entry_note.delete(0, "end")
            self.refresh_data()
            messagebox.showinfo("成功", f"成功入庫\n批號: {batch}\n效期: {expiry}")
        else:
            messagebox.showerror("失敗", msg)