# ... (前段 import 與 create_form 等程式碼都跟上一版一樣，只有 on_product_selected 有變動)
# 為了避免您複製貼上出錯，我這裡只貼出修改後的 on_product_selected 函式
# 但為了方便，我還是提供完整檔案內容

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from ui.theme import Color, Font
from logic.products_logic import get_product_dropdown_list, get_product_shelf_life
from logic.production_logic import add_production_log, get_production_history, generate_batch_number

class ProductionPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="產品生產 Production Log", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 操作區
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))
        self.create_form()

        # 3. 歷史紀錄
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_data()

    def create_form(self):
        self.form_card.columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(self.form_card, text="1. 選擇產品", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.combo_product = ctk.CTkComboBox(self.form_card, state="readonly", width=250, command=self.on_product_selected)
        self.combo_product.set("請選擇")
        self.combo_product.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self.form_card, text="2. 生產數量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.entry_qty = ctk.CTkEntry(self.form_card, placeholder_text="例如: 10")
        self.entry_qty.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self.form_card, text="批號 (自動生成)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_batch = ctk.CTkEntry(self.form_card, placeholder_text="請先選擇產品")
        self.entry_batch.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(self.form_card, text="有效日期 (Expiry)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.entry_expiry = ctk.CTkEntry(self.form_card)
        self.entry_expiry.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(self.form_card, text="備註", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=2, padx=20, pady=(10, 5), sticky="w")
        self.entry_note = ctk.CTkEntry(self.form_card)
        self.entry_note.grid(row=3, column=2, padx=20, pady=(0, 20), sticky="ew")

        self.btn_submit = ctk.CTkButton(self.form_card, text="確認生產", fg_color=Color.PRIMARY, hover_color=Color.PRIMARY_HOVER, font=Font.BODY, height=40, command=self.handle_submit)
        self.btn_submit.grid(row=3, column=3, padx=20, pady=(0, 20), sticky="ew")

    def create_table(self):
        columns = ("date", "name", "qty", "batch", "expiry", "note")
        headers = ["生產時間", "產品名稱", "數量", "批號", "有效期限", "備註"]
        widths = [150, 200, 80, 150, 120, 150]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, font=Font.SMALL)
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
        products = get_product_dropdown_list()
        if products:
            self.combo_product.configure(values=products)
            self.combo_product.set("請選擇產品")
        else:
            self.combo_product.set("無產品資料")

        new_batch = generate_batch_number(None) # 初始無ID
        self.entry_batch.delete(0, "end")
        self.entry_batch.insert(0, new_batch)

        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = get_production_history()
        for row in rows:
            values = (row['date'], row['name'], row['qty'], row['batch_number'], row['expiry_date'], row['note'])
            self.tree.insert("", "end", values=values)

    def on_product_selected(self, val):
        """當選到產品時：1. 算效期 2. 產生批號"""
        if "請選擇" in val or not val: return
        
        try:
            prod_id = int(val.split(" - ")[0])
            
            # --- 1. 計算效期 (如果沒設定 shelf_life，就清空欄位) ---
            days = get_product_shelf_life(prod_id)
            self.entry_expiry.delete(0, "end")
            
            if days:
                expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                self.entry_expiry.insert(0, expiry_date)
            else:
                # 沒設定期限，留空
                pass

            # --- 2. 產生批號 (需傳入 prod_id) ---
            new_batch = generate_batch_number(prod_id)
            self.entry_batch.delete(0, "end")
            self.entry_batch.insert(0, new_batch)

        except Exception as e:
            print(f"Error in on_product_selected: {e}")

    def handle_submit(self):
        prod_str = self.combo_product.get()
        qty_str = self.entry_qty.get()
        batch = self.entry_batch.get()
        expiry = self.entry_expiry.get()
        note = self.entry_note.get()

        if "請選擇" in prod_str or not prod_str:
            messagebox.showwarning("警告", "請選擇產品")
            return
        if not qty_str:
            messagebox.showwarning("警告", "請輸入數量")
            return

        try:
            prod_id = int(prod_str.split(" - ")[0])
            qty = float(qty_str)
        except:
            messagebox.showerror("錯誤", "格式錯誤")
            return

        success, msg = add_production_log(prod_id, qty, batch, expiry, note)
        
        if success:
            messagebox.showinfo("成功", f"生產登錄成功！\n批號: {batch}")
            self.entry_qty.delete(0, "end")
            self.entry_note.delete(0, "end")
            self.refresh_data()
            self.on_product_selected(prod_str)
        else:
            messagebox.showerror("失敗", msg)