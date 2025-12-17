import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from ui.theme import Color, Font, Layout
from logic.products_logic import get_product_dropdown_list, get_product_shelf_life
from logic.production_logic import add_production_log, get_production_history, generate_batch_number

class ProductionPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 15))
        self.create_form()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="生產作業登錄", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(Layout.CARD_PADDING, 10))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, Layout.CARD_PADDING))
        content.columnconfigure((0, 1, 2), weight=1)

        def create_field(parent, label, row, col):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 2: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            e = ctk.CTkEntry(f, height=35)
            e.pack(fill="x")
            return e
        
        def create_combo(parent, label, row, col):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 2: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            c = ctk.CTkComboBox(f, height=35, state="readonly")
            c.pack(fill="x")
            return c

        # Row 0
        self.combo_product = create_combo(content, "1. 選擇產品", 0, 0)
        self.combo_product.configure(command=self.on_product_selected)
        
        self.entry_qty = create_field(content, "2. 生產數量", 0, 1)
        self.entry_note = create_field(content, "備註", 0, 2)

        # Row 1
        self.entry_batch = create_field(content, "批號 (自動生成)", 1, 0)
        self.entry_expiry = create_field(content, "有效日期 (YYYY-MM-DD)", 1, 1)

        # 按鈕 (Row 2)
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="e")
        self.btn_submit = ctk.CTkButton(btn_row, text="確認生產", fg_color=Color.PRIMARY, width=140, height=38, command=self.handle_submit)
        self.btn_submit.pack(side="right")

    def create_table(self):
        columns = ("date", "name", "qty", "batch", "expiry", "note")
        headers = ["生產時間", "產品名稱", "數量", "批號", "有效期限", "備註"]
        widths = [150, 200, 80, 150, 120, 150]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths): self.tree.heading(col, text=h); self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        scroll_y = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scroll_y.set); scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        products = get_product_dropdown_list()
        if products: self.combo_product.configure(values=products); self.combo_product.set("請選擇產品")
        else: self.combo_product.set("無產品資料")
        new_batch = generate_batch_number(None); self.entry_batch.delete(0, "end"); self.entry_batch.insert(0, new_batch)
        self.entry_expiry.delete(0, "end")
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_production_history()
        for i, row in enumerate(rows):
            values = (row['date'], row['name'], row['qty'], row['batch_number'], row['expiry_date'], row['note'])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def on_product_selected(self, val):
        if "請選擇" in val or not val: return
        try:
            prod_id = int(val.split(" - ")[0])
            new_batch = generate_batch_number(prod_id)
            self.entry_batch.delete(0, "end"); self.entry_batch.insert(0, new_batch)
            days = get_product_shelf_life(prod_id)
            self.entry_expiry.delete(0, "end")
            if days is not None:
                target_date = datetime.now() + timedelta(days=days)
                self.entry_expiry.insert(0, target_date.strftime("%Y-%m-%d"))
            else: self.entry_expiry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        except Exception as e: print(f"Error: {e}")

    def handle_submit(self):
        prod_str = self.combo_product.get(); qty_str = self.entry_qty.get(); batch = self.entry_batch.get(); note = self.entry_note.get(); expiry = self.entry_expiry.get()
        if "請選擇" in prod_str or not prod_str: messagebox.showwarning("警告", "請選擇產品"); return
        if not qty_str: messagebox.showwarning("警告", "請輸入數量"); return
        if not expiry: messagebox.showwarning("警告", "請填寫有效日期"); return
        try: prod_id = int(prod_str.split(" - ")[0]); qty = float(qty_str)
        except: messagebox.showerror("錯誤", "格式錯誤"); return
        success, msg = add_production_log(prod_id, qty, batch, expiry, note)
        if success:
            messagebox.showinfo("成功", f"生產登錄成功！\n批號: {batch}")
            self.entry_qty.delete(0, "end"); self.entry_note.delete(0, "end"); self.refresh_data(); self.on_product_selected(prod_str)
        else: messagebox.showerror("失敗", msg)