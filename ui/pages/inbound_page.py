import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font, Layout
from logic.inbound_logic import add_inbound_record, get_inbound_history
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category

class InboundPage(ctk.CTkFrame):
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
        ctk.CTkLabel(self.form_card, text="入庫登錄", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2), weight=1)
        
        # 第一排
        ctk.CTkLabel(content, text="1. 類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_category = ctk.CTkComboBox(content, state="readonly", command=self.on_category_change)
        self.combo_category.set("請選擇")
        self.combo_category.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="2. 品項", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.combo_material = ctk.CTkComboBox(content, state="readonly")
        self.combo_material.set("請先選擇類別")
        self.combo_material.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="入庫數量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_qty = ctk.CTkEntry(content, placeholder_text="輸入數字")
        self.entry_qty.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        # 第二排
        ctk.CTkLabel(content, text="批號 (選填)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_batch = ctk.CTkEntry(content, placeholder_text="例如：B20251212")
        self.entry_batch.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="有效期限 (YYYY-MM-DD)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.entry_expiry = ctk.CTkEntry(content, placeholder_text="供過期警示用")
        self.entry_expiry.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.entry_note = ctk.CTkEntry(content, placeholder_text="選填")
        self.entry_note.grid(row=3, column=2, padx=10, pady=(0, 10), sticky="ew")

        # 按鈕：移到右下角，固定寬度
        self.btn_submit = ctk.CTkButton(content, text="確認入庫", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_submit)
        self.btn_submit.grid(row=4, column=2, padx=10, pady=(10, 20), sticky="e")

    def create_table(self):
        columns = ("date", "name", "brand", "qty", "unit", "batch", "expiry", "note")
        headers = ["入庫時間", "原料名稱", "廠牌", "數量", "單位", "批號", "有效期限", "備註"]
        widths = [140, 140, 100, 60, 50, 100, 100, 150]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white")
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header); self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        categories = get_existing_categories()
        if categories: self.combo_category.configure(values=categories); self.combo_category.set("請選擇類別")
        else: self.combo_category.configure(values=["無資料"]); self.combo_category.set("無資料")
        self.combo_material.set(""); self.combo_material.configure(values=[])

        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_inbound_history()
        for row in rows:
            values = (row['date'], row['name'], row['brand'], row['qty'], row['unit'], row['batch_number'], row['expiry_date'], row['note'])
            self.tree.insert("", "end", values=values)

    def on_category_change(self, selected_category):
        if not selected_category or selected_category == "請選擇類別": return
        materials = get_materials_by_category(selected_category)
        if materials: self.combo_material.configure(values=materials); self.combo_material.set(materials[0])
        else: self.combo_material.configure(values=["此類別無原料"]); self.combo_material.set("此類別無原料")

    def handle_submit(self):
        selected_str = self.combo_material.get(); qty_str = self.entry_qty.get(); batch = self.entry_batch.get(); expiry = self.entry_expiry.get(); note = self.entry_note.get()
        if not selected_str or "無原料" in selected_str or "請先選擇" in selected_str: messagebox.showwarning("警告", "請選擇有效的原料"); return
        if not qty_str: messagebox.showwarning("警告", "請輸入數量"); return
        try: material_id = int(selected_str.split(" - ")[0]); qty = float(qty_str)
        except: messagebox.showerror("錯誤", "數量格式錯誤"); return
        success, msg = add_inbound_record(material_id, qty, batch, expiry, note)
        if success:
            self.entry_qty.delete(0, "end"); self.entry_batch.delete(0, "end"); self.entry_expiry.delete(0, "end"); self.entry_note.delete(0, "end")
            self.refresh_data(); messagebox.showinfo("成功", f"成功入庫 {qty} 單位")
        else: messagebox.showerror("失敗", msg)