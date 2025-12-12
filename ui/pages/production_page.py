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
        self.form_card.pack(fill="x", pady=(20, 20))
        self.create_form()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="生產作業登錄", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2), weight=1)
        
        def add_field(label, r, c):
            ctk.CTkLabel(content, text=label, font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=r*2, column=c, padx=Layout.GRID_PADX, pady=(5, 0), sticky="w")

        add_field("1. 選擇產品", 0, 0); self.combo_product = ctk.CTkComboBox(content, state="readonly", width=250, command=self.on_product_selected); self.combo_product.set("請選擇"); self.combo_product.grid(row=1, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        add_field("2. 生產數量", 0, 1); self.entry_qty = ctk.CTkEntry(content, placeholder_text="例如: 10"); self.entry_qty.grid(row=1, column=1, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        add_field("備註", 0, 2); self.entry_note = ctk.CTkEntry(content); self.entry_note.grid(row=1, column=2, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")

        add_field("批號 (自動生成)", 1, 0); self.entry_batch = ctk.CTkEntry(content, placeholder_text="請先選擇產品"); self.entry_batch.grid(row=3, column=0, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        
        add_field("有效日期 (YYYY/MM/DD)", 1, 1)
        date_frame = ctk.CTkFrame(content, fg_color="transparent"); date_frame.grid(row=3, column=1, padx=Layout.GRID_PADX, pady=Layout.GRID_PADY, sticky="ew")
        current_year = datetime.now().year; years = [str(y) for y in range(current_year, current_year + 5)]; months = [f"{m:02d}" for m in range(1, 13)]; days = [f"{d:02d}" for d in range(1, 32)]
        
        self.combo_year = ctk.CTkComboBox(date_frame, values=years, width=80, state="readonly"); self.combo_year.set(str(current_year)); self.combo_year.pack(side="left", padx=(0, 5))
        self.combo_month = ctk.CTkComboBox(date_frame, values=months, width=60, state="readonly"); self.combo_month.set(datetime.now().strftime("%m")); self.combo_month.pack(side="left", padx=5)
        self.combo_day = ctk.CTkComboBox(date_frame, values=days, width=60, state="readonly"); self.combo_day.set(datetime.now().strftime("%d")); self.combo_day.pack(side="left", padx=5)

        self.btn_submit = ctk.CTkButton(content, text="確認生產", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_submit)
        self.btn_submit.grid(row=3, column=2, padx=Layout.GRID_PADX, pady=(10, 20), sticky="e")

    def create_table(self):
        columns = ("date", "name", "qty", "batch", "expiry", "note")
        headers = ["生產時間", "產品名稱", "數量", "批號", "有效期限", "備註"]
        widths = [150, 200, 80, 150, 120, 150]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths): self.tree.heading(col, text=h); self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5); self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_data(self):
        products = get_product_dropdown_list()
        if products: self.combo_product.configure(values=products); self.combo_product.set("請選擇產品")
        else: self.combo_product.set("無產品資料")
        new_batch = generate_batch_number(None); self.entry_batch.delete(0, "end"); self.entry_batch.insert(0, new_batch)
        
        # 重置日期為今天
        now = datetime.now()
        self.combo_year.set(str(now.year))
        self.combo_month.set(f"{now.month:02d}")
        self.combo_day.set(f"{now.day:02d}")

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
            
            # 1. 產生批號
            new_batch = generate_batch_number(prod_id)
            self.entry_batch.delete(0, "end"); self.entry_batch.insert(0, new_batch)

            # 2. 自動計算效期並更新下拉選單
            days = get_product_shelf_life(prod_id)
            if days:
                target_date = datetime.now() + timedelta(days=days)
                # ⚠️ 關鍵修正：更新下拉選單的值
                self.combo_year.set(str(target_date.year))
                self.combo_month.set(f"{target_date.month:02d}")
                self.combo_day.set(f"{target_date.day:02d}")
                
        except Exception as e: print(f"Error: {e}")

    def handle_submit(self):
        prod_str = self.combo_product.get(); qty_str = self.entry_qty.get(); batch = self.entry_batch.get(); note = self.entry_note.get()
        
        # 組合日期字串
        y = self.combo_year.get()
        m = self.combo_month.get()
        d = self.combo_day.get()
        expiry = f"{y}-{m}-{d}"

        if "請選擇" in prod_str or not prod_str: messagebox.showwarning("警告", "請選擇產品"); return
        if not qty_str: messagebox.showwarning("警告", "請輸入數量"); return
        try: prod_id = int(prod_str.split(" - ")[0]); qty = float(qty_str)
        except: messagebox.showerror("錯誤", "格式錯誤"); return
        
        success, msg = add_production_log(prod_id, qty, batch, expiry, note)
        if success:
            messagebox.showinfo("成功", f"生產登錄成功！\n批號: {batch}")
            self.entry_qty.delete(0, "end"); self.entry_note.delete(0, "end")
            self.refresh_data()
            self.on_product_selected(prod_str) # 重新觸發以更新批號
        else: messagebox.showerror("失敗", msg)