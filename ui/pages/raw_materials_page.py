import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.raw_materials_logic import add_material, get_all_materials, delete_material
from ui.theme import Color, Font

class RawMaterialsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 頁面標題
        title = ctk.CTkLabel(
            self, 
            text="原料管理 Raw Materials", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 輸入區塊
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))

        self.create_form()

        # 3. 列表區塊
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)

        self.create_table()
        
        # 載入資料
        self.refresh_table()

    def create_form(self):
        # 讓欄位排版稍微寬鬆一點，使用 Grid
        self.form_card.columnconfigure((0, 1, 2), weight=1)
        
        # --- 第一排 ---
        # 1. 名稱
        ctk.CTkLabel(self.form_card, text="名稱", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_name = ctk.CTkEntry(self.form_card, placeholder_text="例如：日本鑽石麵粉")
        self.entry_name.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. 類別
        ctk.CTkLabel(self.form_card, text="類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.combo_category = ctk.CTkComboBox(
            self.form_card, 
            values=["粉類", "糖類", "油脂類", "乳製品", "巧克力", "乾果/堅果", "添加物/香料", "包材", "其他"],
            state="readonly"
        )
        self.combo_category.set("粉類")
        self.combo_category.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="ew")

        # 3. 廠牌 (Brand)
        ctk.CTkLabel(self.form_card, text="廠牌", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=20, pady=(20, 5), sticky="w")
        self.entry_brand = ctk.CTkEntry(self.form_card, placeholder_text="例如：日本製粉")
        self.entry_brand.grid(row=1, column=2, padx=20, pady=(0, 10), sticky="ew")

        # --- 第二排 ---
        # 4. 廠商 (Vendor) - 新增
        ctk.CTkLabel(self.form_card, text="廠商", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.combo_vendor = ctk.CTkComboBox(
            self.form_card,
            values=["苗林行", "開元食品", "德麥食品", "富華", "聯華製粉", "自行採購"], # 常見供應商
            # 注意：這裡不設 state="readonly"，所以使用者可以自己打字新增
        )
        self.combo_vendor.set("苗林行") # 預設值
        self.combo_vendor.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # 5. 單位 (Unit) - 改為下拉
        ctk.CTkLabel(self.form_card, text="單位", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.combo_unit = ctk.CTkComboBox(
            self.form_card,
            values=["kg", "g", "ml", "L", "罐", "個", "包", "箱", "台斤"],
            # 這裡也可以讓使用者自己打，或者鎖定，看您的需求。目前設為可手動輸入。
        )
        self.combo_unit.set("kg") 
        self.combo_unit.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")

        # 6. 安全庫存 (不預設值)
        ctk.CTkLabel(self.form_card, text="安全庫存", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=2, padx=20, pady=(10, 5), sticky="w")
        self.entry_safe = ctk.CTkEntry(self.form_card, placeholder_text="請輸入數字")
        self.entry_safe.grid(row=3, column=2, padx=20, pady=(0, 20), sticky="ew")

        # --- 按鈕區 (獨立一排或放旁邊) ---
        self.btn_add = ctk.CTkButton(
            self.form_card, 
            text="＋ 新增原料", 
            fg_color=Color.PRIMARY, 
            hover_color=Color.PRIMARY_HOVER,
            font=Font.BODY,
            height=40,
            command=self.handle_add
        )
        # 讓按鈕在最下方跨欄顯示，比較大氣
        self.btn_add.grid(row=4, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="ew")

    def create_table(self):
        # 定義欄位 (新增 vendor)
        columns = ("id", "name", "category", "brand", "vendor", "unit", "stock", "safe_stock")
        headers = ["ID", "名稱", "類別", "廠牌", "廠商", "單位", "目前庫存", "安全庫存"]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", rowheight=30, font=("Microsoft JhengHei UI", 12))
        style.configure("Treeview.Heading", font=("Microsoft JhengHei UI", 12, "bold"))
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        
        # 設定欄寬
        widths = [40, 150, 80, 100, 100, 60, 80, 80]
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def handle_add(self):
        name = self.entry_name.get()
        category = self.combo_category.get()
        brand = self.entry_brand.get()
        vendor = self.combo_vendor.get() # 取得廠商
        unit = self.combo_unit.get()     # 取得單位
        safe_stock = self.entry_safe.get()

        if not name or not unit:
            messagebox.showwarning("欄位未填", "請填寫名稱與單位！")
            return

        # 處理安全庫存輸入
        try:
            val_safe = float(safe_stock) if safe_stock else 0.0
        except ValueError:
            messagebox.showerror("格式錯誤", "安全庫存必須是數字")
            return

        success, msg = add_material(name, category, brand, vendor, unit, val_safe)
        
        if success:
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showerror("錯誤", msg)

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_brand.delete(0, "end")
        self.entry_safe.delete(0, "end")
        # 下拉選單通常不用特別清空，維持預設或上次選擇即可，方便連續輸入
        # self.combo_vendor.set("苗林行") 
        # self.combo_unit.set("kg")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        rows = get_all_materials()
        for row in rows:
            # 確保順序對應: id, name, category, brand, vendor, unit, stock, safe_stock
            values = (row['id'], row['name'], row['category'], row['brand'], row['vendor'], row['unit'], row['stock'], row['safe_stock'])
            self.tree.insert("", "end", values=values)