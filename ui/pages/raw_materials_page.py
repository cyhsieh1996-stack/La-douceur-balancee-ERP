import customtkinter as ctk
from tkinter import ttk  # 引入原生套件來做表格
from logic.materials_logic import add_material, get_all_materials, delete_material
from ui.theme import Color, Font

class RawMaterialsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent") # 透出底色

        # ==========================
        # 1. 標題
        # ==========================
        title = ctk.CTkLabel(
            self, 
            text="原料管理 Raw Materials", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # ==========================
        # 2. 新增原料區塊 (白色卡片)
        # ==========================
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))

        self.create_form()

        # ==========================
        # 3. 原料列表區塊 (白色卡片)
        # ==========================
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)

        self.create_table()
        
        # 初始載入資料
        self.refresh_table()

    def create_form(self):
        """建立輸入表單"""
        # 使用 Grid 佈局讓欄位整齊排列
        self.form_card.columnconfigure((0, 1, 2, 3), weight=1)
        
        # --- 第一排 ---
        # 1. 名稱
        ctk.CTkLabel(self.form_card, text="名稱", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_name = ctk.CTkEntry(self.form_card, placeholder_text="例如：日本鑽石麵粉")
        self.entry_name.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 2. 類別 (下拉選單)
        ctk.CTkLabel(self.form_card, text="類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.combo_category = ctk.CTkComboBox(
            self.form_card, 
            values=["粉類", "糖類", "油脂類", "乳製品", "巧克力", "乾果/堅果", "添加物/香料", "包材", "其他"],
            state="readonly" # 禁止手動輸入，只能選
        )
        self.combo_category.set("粉類") # 預設值
        self.combo_category.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="ew")

        # 3. 廠牌
        ctk.CTkLabel(self.form_card, text="廠牌", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=20, pady=(20, 5), sticky="w")
        self.entry_brand = ctk.CTkEntry(self.form_card, placeholder_text="例如：日本製粉")
        self.entry_brand.grid(row=1, column=2, padx=20, pady=(0, 10), sticky="ew")

        # --- 第二排 ---
        # 4. 單位
        ctk.CTkLabel(self.form_card, text="單位", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_unit = ctk.CTkEntry(self.form_card, placeholder_text="g, kg, ml, 個")
        self.entry_unit.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # 5. 安全庫存
        ctk.CTkLabel(self.form_card, text="安全庫存", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.entry_safe = ctk.CTkEntry(self.form_card, placeholder_text="預設 50")
        self.entry_safe.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")

        # 6. 按鈕區
        self.btn_add = ctk.CTkButton(
            self.form_card, 
            text="＋ 新增原料", 
            fg_color=Color.PRIMARY, 
            hover_color=Color.PRIMARY_HOVER,
            font=Font.BODY,
            height=36,
            command=self.handle_add
        )
        self.btn_add.grid(row=3, column=2, padx=20, pady=(0, 20), sticky="ew")

    def create_table(self):
        """建立列表表格 (使用 Treeview)"""
        # 定義欄位
        columns = ("id", "name", "category", "brand", "unit", "stock", "safe_stock")
        
        # 設定 Treeview 樣式 (讓它長得比較現代)
        style = ttk.Style()
        style.theme_use("clam") # 使用較乾淨的基礎樣式
        style.configure(
            "Treeview", 
            background="white",
            foreground=Color.TEXT_DARK, 
            rowheight=30, 
            fieldbackground="white",
            font=("Microsoft JhengHei UI", 12)
        )
        style.configure(
            "Treeview.Heading", 
            font=("Microsoft JhengHei UI", 12, "bold"),
            background="#F0F0F0",
            foreground=Color.TEXT_DARK
        )
        style.map("Treeview", background=[('selected', Color.PRIMARY)])

        # 建立表格
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings", style="Treeview")
        
        # 設定中文表頭
        headers = ["ID", "名稱", "類別", "廠牌", "單位", "目前庫存", "安全庫存"]
        widths = [40, 150, 80, 100, 60, 80, 80]
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")
        
        # 調整 "名稱" 欄位靠左對齊，比較好看
        self.tree.column("name", anchor="w", width=200)

        # 捲軸
        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def handle_add(self):
        name = self.entry_name.get()
        category = self.combo_category.get()
        brand = self.entry_brand.get()
        unit = self.entry_unit.get()
        safe_stock = self.entry_safe.get()

        if not name or not unit:
            print("請填寫必填欄位") # 之後可以用彈窗提示
            return

        if not safe_stock:
            safe_stock = 50

        success, msg = add_material(name, category, brand, unit, float(safe_stock))
        
        if success:
            self.clear_form()
            self.refresh_table()
        else:
            print(f"Error: {msg}")

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_brand.delete(0, "end")
        self.entry_unit.delete(0, "end")
        self.entry_safe.delete(0, "end")

    def refresh_table(self):
        # 清空舊資料
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 載入新資料
        rows = get_all_materials()
        for row in rows:
            # row 是一個 sqlite3.Row 物件，依序轉成 tuple
            # DB 順序: id, name, category, brand, unit, stock, safe_stock
            values = (row['id'], row['name'], row['category'], row['brand'], row['unit'], row['stock'], row['safe_stock'])
            self.tree.insert("", "end", values=values)