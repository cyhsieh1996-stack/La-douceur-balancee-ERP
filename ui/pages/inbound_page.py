import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from ui.theme import Color, Font
from logic.materials_logic import get_all_materials 
from logic.inbound_logic import add_inbound_record, get_recent_inbound_records
from ui.input_utils import clean_text, parse_non_negative_float, parse_positive_float, validate_date_yyyy_mm_dd

class InboundPage(ctk.CTkFrame):
    LAST_CATEGORY = ""
    LAST_MATERIAL = ""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # --- 1. 標題區 ---
        ctk.CTkLabel(self, text="原料入庫登錄", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 20))

        # --- 2. 表單區 (白色卡片) ---
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))
        
        self.create_form()

        # --- 3. 歷史紀錄標題 ---
        ctk.CTkLabel(self, text="最近入庫紀錄 (Latest 20)", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(10, 10))

        # --- 4. 歷史紀錄表格 (白色卡片) ---
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        
        self.create_history_table()
        
        # 初始載入
        self.load_material_data()
        self.refresh_table()
        self.bind_submit_shortcuts()
        self.qty_entry.focus_set()

    def create_form(self):
        # 表單容器
        form_container = ctk.CTkFrame(self.form_card, fg_color="transparent")
        form_container.pack(fill="x", padx=20, pady=20)
        
        lbl_style = {"font": Font.BODY, "text_color": Color.TEXT_DARK, "anchor": "w"}

        # --- 第一排：類別、品項 ---
        ctk.CTkLabel(form_container, text="類別", **lbl_style).grid(row=0, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(form_container, text="品項", **lbl_style).grid(row=0, column=1, padx=10, pady=(0, 5), sticky="w")
        
        self.category_cb = ctk.CTkComboBox(form_container, values=["請選擇類別"], width=180, command=self.on_category_change, state="readonly")
        self.category_cb.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="w")
        
        self.material_cb = ctk.CTkComboBox(form_container, values=[], width=250, state="readonly")
        self.material_cb.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="w")

        # --- 第二排：入庫數量、進貨單價 ---
        ctk.CTkLabel(form_container, text="入庫數量", **lbl_style).grid(row=0, column=2, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(form_container, text="進貨單價", **lbl_style).grid(row=0, column=3, padx=10, pady=(0, 5), sticky="w")
        
        self.qty_entry = ctk.CTkEntry(form_container, width=120, placeholder_text="例如: 10")
        self.qty_entry.grid(row=1, column=2, padx=10, pady=(0, 15), sticky="w")
        
        self.price_entry = ctk.CTkEntry(form_container, width=120, placeholder_text="單價")
        self.price_entry.grid(row=1, column=3, padx=10, pady=(0, 15), sticky="w")

        # --- 第三排：批號、有效期限 (加寬版) ---
        ctk.CTkLabel(form_container, text="批號 (選填)", **lbl_style).grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(form_container, text="有效期限", **lbl_style).grid(row=2, column=1, padx=10, pady=(0, 5), sticky="w")
        
        self.batch_entry = ctk.CTkEntry(form_container, width=180)
        self.batch_entry.grid(row=3, column=0, padx=10, pady=(0, 15), sticky="w")

        # 日期選擇容器
        date_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        date_frame.grid(row=3, column=1, padx=10, pady=(0, 15), sticky="w")
        
        today = datetime.now()
        years = [str(y) for y in range(today.year, today.year + 10)]
        months = [str(m).zfill(2) for m in range(1, 13)]
        days = [str(d).zfill(2) for d in range(1, 32)]
        
        self.year_cb = ctk.CTkComboBox(date_frame, values=years, width=100, state="readonly")
        self.year_cb.pack(side="left", padx=(0, 5))
        self.year_cb.set(str(today.year))
        
        self.month_cb = ctk.CTkComboBox(date_frame, values=months, width=80, state="readonly")
        self.month_cb.pack(side="left", padx=5)
        self.month_cb.set(str(today.month).zfill(2))
        
        self.day_cb = ctk.CTkComboBox(date_frame, values=days, width=80, state="readonly")
        self.day_cb.pack(side="left", padx=5)
        self.day_cb.set(str(today.day).zfill(2))

        # --- 第四排：備註、按鈕 ---
        ctk.CTkLabel(form_container, text="備註", **lbl_style).grid(row=2, column=2, columnspan=2, padx=10, pady=(0, 5), sticky="w")
        
        self.note_entry = ctk.CTkEntry(form_container, width=250)
        self.note_entry.grid(row=3, column=2, columnspan=2, padx=10, pady=(0, 15), sticky="we")

        self.btn_submit = ctk.CTkButton(form_container, text="確認入庫", fg_color=Color.PRIMARY, width=120, height=38, command=self.submit)
        self.btn_submit.grid(row=3, column=4, padx=10, pady=(0, 15), sticky="e")

    def bind_submit_shortcuts(self):
        self.qty_entry.bind("<Return>", lambda _e: self.price_entry.focus_set())
        self.price_entry.bind("<Return>", lambda _e: self.batch_entry.focus_set())
        self.batch_entry.bind("<Return>", lambda _e: self.note_entry.focus_set())
        self.note_entry.bind("<Return>", lambda _e: self.submit())

    def create_history_table(self):
        # 表格容器
        table_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("date", "name", "qty", "unit", "batch", "expiry")
        headers = ["入庫時間", "原料名稱", "入庫數量", "單位", "批號", "有效期限"]
        widths = [140, 180, 80, 60, 120, 100]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")

        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="none")
        
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")

        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def load_material_data(self):
        # 載入所有原料
        self.materials = get_all_materials()
        self.cat_map = {}
        for m in self.materials:
            cat = m.get('category', '未分類') or '未分類'
            if cat not in self.cat_map:
                self.cat_map[cat] = []
            self.cat_map[cat].append(m['name'])
            
        cats = list(self.cat_map.keys())
        self.category_cb.configure(values=cats)
        if cats:
            default_cat = self.LAST_CATEGORY if self.LAST_CATEGORY in cats else cats[0]
            self.category_cb.set(default_cat)
            self.on_category_change(None)

    def on_category_change(self, event):
        cat = self.category_cb.get()
        items = self.cat_map.get(cat, [])
        self.material_cb.configure(values=items)
        if items:
            default_material = self.LAST_MATERIAL if self.LAST_MATERIAL in items else items[0]
            self.material_cb.set(default_material)
        else: self.material_cb.set("")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        records = get_recent_inbound_records(limit=20)
        for i, row in enumerate(records):
            # row: date, name, qty, unit, batch, expiry
            date_str = row[0]
            if len(date_str) > 16: date_str = date_str[:16]
            
            vals = (date_str, row[1], row[2], row[3], row[4], row[5])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def submit(self):
        name = clean_text(self.material_cb.get())
        qty = self.qty_entry.get()
        price = self.price_entry.get()
        batch = clean_text(self.batch_entry.get())
        expiry = f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}"
        note = clean_text(self.note_entry.get())

        if not name or not qty:
            messagebox.showwarning("警告", "請選擇品項並填寫數量")
            return
        qty_val, err = parse_positive_float(qty, "入庫數量")
        if err:
            messagebox.showerror("錯誤", err)
            return
        price_val, err = parse_non_negative_float(price, "進貨單價")
        if err:
            messagebox.showerror("錯誤", err)
            return
        if not validate_date_yyyy_mm_dd(expiry):
            messagebox.showerror("錯誤", "有效期限日期格式不正確")
            return
        
        mat_id = next((m['id'] for m in self.materials if m['name'] == name), None)
        
        if mat_id:
            success, msg = add_inbound_record(mat_id, qty_val, price_val, batch, expiry, note)
            if success:
                self.__class__.LAST_CATEGORY = self.category_cb.get()
                self.__class__.LAST_MATERIAL = name
                messagebox.showinfo("成功", msg)
                self.qty_entry.delete(0, "end")
                self.price_entry.delete(0, "end")
                self.batch_entry.delete(0, "end")
                self.note_entry.delete(0, "end")
                self.qty_entry.focus_set()
                self.refresh_table()
            else:
                messagebox.showerror("錯誤", msg)
        else:
            messagebox.showerror("錯誤", "系統錯誤：找不到原料 ID")
