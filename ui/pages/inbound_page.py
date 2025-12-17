import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.theme import Color, Font, Layout
from logic.inbound_logic import add_inbound_record, get_inbound_history
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category

class InboundPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.form_card.pack(fill="x", pady=(10, 10))
        self.create_form()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="入庫登錄", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(10, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, 10))
        content.columnconfigure((0, 1, 2, 3), weight=1)

        def create_field(parent, label, row, col):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
            e = ctk.CTkEntry(f, height=Layout.BTN_HEIGHT)
            e.pack(fill="x")
            return e
        
        def create_combo(parent, label, row, col):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: f.grid_configure(padx=(0, 0))
            ctk.CTkLabel(f, text=label, font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
            c = ctk.CTkComboBox(f, height=Layout.BTN_HEIGHT, state="readonly")
            c.pack(fill="x")
            return c

        # Row 0
        self.combo_category = create_combo(content, "類別", 0, 0)
        self.combo_category.configure(command=self.on_category_change)
        
        self.combo_material = create_combo(content, "品項", 0, 1)
        self.entry_qty = create_field(content, "入庫數量", 0, 2)
        self.entry_price = create_field(content, "進貨單價", 0, 3)

        # Row 1
        self.entry_batch = create_field(content, "批號 (選填)", 1, 0)
        
        # Date
        date_wrapper = ctk.CTkFrame(content, fg_color="transparent")
        date_wrapper.grid(row=1, column=1, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
        ctk.CTkLabel(date_wrapper, text="有效期限", font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
        
        d_box = ctk.CTkFrame(date_wrapper, fg_color="transparent")
        d_box.pack(fill="x")
        
        current_year = datetime.now().year
        self.combo_year = ctk.CTkComboBox(d_box, values=[str(y) for y in range(current_year, current_year+10)], width=75, height=Layout.BTN_HEIGHT)
        self.combo_year.pack(side="left", padx=(0, 5))
        self.combo_year.set(str(current_year))
        
        self.combo_month = ctk.CTkComboBox(d_box, values=[f"{m:02d}" for m in range(1, 13)], width=65, height=Layout.BTN_HEIGHT)
        self.combo_month.pack(side="left", padx=5)
        self.combo_month.set(datetime.now().strftime("%m"))
        
        self.combo_day = ctk.CTkComboBox(d_box, values=[f"{d:02d}" for d in range(1, 32)], width=65, height=Layout.BTN_HEIGHT)
        self.combo_day.pack(side="left", padx=5)
        self.combo_day.set(datetime.now().strftime("%d"))

        # Note
        note_wrapper = ctk.CTkFrame(content, fg_color="transparent")
        note_wrapper.grid(row=1, column=2, columnspan=2, padx=(0, 0), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
        ctk.CTkLabel(note_wrapper, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
        self.entry_note = ctk.CTkEntry(note_wrapper, height=Layout.BTN_HEIGHT)
        self.entry_note.pack(fill="x")

        # Btn (Row 2)
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=4, pady=(5, 0), sticky="e")
        self.btn_submit = ctk.CTkButton(btn_row, text="確認入庫", fg_color=Color.PRIMARY, width=120, height=Layout.BTN_HEIGHT, command=self.handle_submit)
        self.btn_submit.pack(side="right")

    def create_table(self):
        columns = ("date", "name", "brand", "qty", "unit", "price", "batch", "expiry", "note")
        headers = ["入庫時間", "原料名稱", "廠牌", "數量", "單位", "單價", "批號", "有效期限", "備註"]
        widths = [140, 140, 100, 60, 50, 60, 100, 100, 150]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        scroll_y = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(self.table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)
        scroll_x.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        cats = get_existing_categories()
        if cats: self.combo_category.configure(values=cats); self.combo_category.set("請選擇類別")
        else: self.combo_category.configure(values=["無資料"]); self.combo_category.set("無資料")
        self.combo_material.set(""); self.combo_material.configure(values=[])

        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_inbound_history()
        for i, row in enumerate(rows):
            values = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def on_category_change(self, selected_category):
        if not selected_category or selected_category == "請選擇類別": return
        materials = get_materials_by_category(selected_category)
        if materials: self.combo_material.configure(values=materials); self.combo_material.set(materials[0])
        else: self.combo_material.configure(values=["此類別無原料"]); self.combo_material.set("此類別無原料")

    def handle_submit(self):
        selected_str = self.combo_material.get()
        qty_str = self.entry_qty.get()
        price_str = self.entry_price.get()
        batch = self.entry_batch.get()
        note = self.entry_note.get()
        
        y = self.combo_year.get()
        m = self.combo_month.get()
        d = self.combo_day.get()
        expiry = f"{y}-{m}-{d}"

        if not selected_str or "無原料" in selected_str or "請先選擇" in selected_str:
            messagebox.showwarning("警告", "請選擇有效的原料")
            return
        if not qty_str:
            messagebox.showwarning("警告", "請輸入數量")
            return

        unit_price = 0
        try:
            material_id = int(selected_str.split(" - ")[0])
            qty = float(qty_str)
            if price_str:
                unit_price = float(price_str)
        except:
            messagebox.showerror("錯誤", "數量或價格格式錯誤")
            return

        success, msg = add_inbound_record(material_id, qty, unit_price, batch, expiry, note)
        
        if success:
            self.entry_qty.delete(0, "end")
            self.entry_price.delete(0, "end")
            self.entry_batch.delete(0, "end")
            self.entry_note.delete(0, "end")
            self.refresh_data()
            messagebox.showinfo("成功", f"成功入庫 {qty} 單位")
        else:
            messagebox.showerror("失敗", msg)