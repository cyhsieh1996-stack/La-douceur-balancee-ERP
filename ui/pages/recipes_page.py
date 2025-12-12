import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.recipes_logic import get_product_list, get_current_recipe, save_recipe_to_db
from logic.raw_materials_logic import get_existing_categories, get_materials_by_category
from ui.theme import Color, Font

class RecipesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.current_ingredients = [] 

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="食譜設定 Recipes (SOP/成本計算)", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 選擇產品
        self.top_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.top_card.pack(fill="x", pady=(0, 15))
        self.create_product_selector()

        # 3. 編輯區
        self.main_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.main_card.pack(fill="both", expand=True)
        
        self.create_ingredient_input()
        self.create_table()
        self.create_footer_actions()

    def create_product_selector(self):
        inner = ctk.CTkFrame(self.top_card, fg_color="transparent")
        inner.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(inner, text="1. 選擇產品：", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(side="left")
        
        self.combo_product = ctk.CTkComboBox(
            inner, 
            width=300, 
            state="readonly",
            command=self.on_product_selected
        )
        self.combo_product.pack(side="left", padx=15)
        
        products = get_product_list()
        if products:
            self.combo_product.configure(values=products)
            self.combo_product.set("請選擇產品")
        else:
            self.combo_product.set("無產品資料")

    def create_ingredient_input(self):
        input_frame = ctk.CTkFrame(self.main_card, fg_color="#F9F9F9", corner_radius=8)
        input_frame.pack(padx=20, pady=20, fill="x")
        
        input_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        # 1. 類別
        ctk.CTkLabel(input_frame, text="原料類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_category = ctk.CTkComboBox(input_frame, state="readonly", width=140, command=self.on_category_change)
        self.combo_category.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        cats = get_existing_categories()
        if cats:
            self.combo_category.configure(values=cats)
            self.combo_category.set("請選擇")

        # 2. 原料
        ctk.CTkLabel(input_frame, text="選擇原料", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.combo_material = ctk.CTkComboBox(input_frame, state="readonly", width=200, command=self.on_material_selected)
        self.combo_material.set("請先選類別")
        self.combo_material.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # 3. 用量
        ctk.CTkLabel(input_frame, text="使用量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_amount = ctk.CTkEntry(input_frame, placeholder_text="數字")
        self.entry_amount.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        # 4. 單位 (改為下拉選單)
        ctk.CTkLabel(input_frame, text="單位", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        self.combo_unit = ctk.CTkComboBox(
            input_frame, 
            values=["g", "kg", "ml", "L", "顆", "個", "罐", "包", "適量", "台斤"],
            width=90
        )
        self.combo_unit.set("g")
        self.combo_unit.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # 5. 加入按鈕
        self.btn_add_item = ctk.CTkButton(
            input_frame, 
            text="⬇ 加入", 
            fg_color=Color.PRIMARY, 
            font=Font.BODY,
            command=self.add_ingredient_to_list
        )
        self.btn_add_item.grid(row=1, column=4, padx=10, pady=5, sticky="ew")

    def create_table(self):
        columns = ("name", "amount", "unit")
        headers = ["原料名稱", "使用量", "單位"]
        widths = [250, 100, 100]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, fieldbackground="white", font=Font.SMALL)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.main_card, columns=columns, show="headings", height=10)
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 10))
        self.tree.bind("<Double-1>", self.on_double_click_delete)
        
        tip = ctk.CTkLabel(self.main_card, text="(提示：雙擊項目可刪除)", text_color=Color.TEXT_LIGHT, font=Font.SMALL)
        tip.pack(anchor="e", padx=20)

    def create_footer_actions(self):
        footer = ctk.CTkFrame(self.main_card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)

        self.btn_save = ctk.CTkButton(
            footer, 
            text="💾 儲存配方 (僅供紀錄)", 
            fg_color="#2CC985",
            hover_color="#25A970",
            font=("Microsoft JhengHei UI", 18, "bold"),
            height=50,
            command=self.save_recipe
        )
        self.btn_save.pack(fill="x")

    def on_category_change(self, category):
        if not category: return
        materials = get_materials_by_category(category)
        if materials:
            self.combo_material.configure(values=materials)
            self.combo_material.set(materials[0])
            self.on_material_selected(materials[0])
        else:
            self.combo_material.configure(values=["無原料"])
            self.combo_material.set("無原料")

    def on_material_selected(self, val):
        """當選到某個原料，嘗試自動切換單位選單"""
        try:
            # val 格式: "1 - 麵粉 (kg)"
            unit_part = val.split("(")[-1].replace(")", "")
            # 如果這個單位在我們的選單裡，就自動選取它
            if unit_part in self.combo_unit._values:
                self.combo_unit.set(unit_part)
        except:
            pass

    def on_product_selected(self, val):
        if "請選擇" in val: return
        product_id = int(val.split(" - ")[0])
        self.current_ingredients = []
        self.refresh_tree()
        
        existing_recipe = get_current_recipe(product_id)
        if existing_recipe:
            for row in existing_recipe:
                self.current_ingredients.append({
                    "id": row[0], "name": row[1], "amount": row[2], "unit": row[3]
                })
            self.refresh_tree()

    def add_ingredient_to_list(self):
        mat_str = self.combo_material.get()
        amount_str = self.entry_amount.get()
        unit = self.combo_unit.get() # 取得下拉選單的值

        if "請先選" in mat_str or "無原料" in mat_str: return
        if not amount_str:
            messagebox.showwarning("警告", "請輸入使用量")
            return

        try:
            mat_id = int(mat_str.split(" - ")[0])
            mat_name = mat_str.split(" - ")[1].split(" (")[0]
            amount = float(amount_str)
        except:
            messagebox.showerror("錯誤", "格式錯誤")
            return

        for item in self.current_ingredients:
            if item["id"] == mat_id:
                item["amount"] += amount
                item["unit"] = unit # 更新單位
                self.refresh_tree()
                self.entry_amount.delete(0, "end")
                return

        self.current_ingredients.append({
            "id": mat_id, "name": mat_name, "amount": amount, "unit": unit
        })
        self.refresh_tree()
        self.entry_amount.delete(0, "end")

    def on_double_click_delete(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        idx = self.tree.index(selected_item[0])
        del self.current_ingredients[idx]
        self.refresh_tree()

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.current_ingredients:
            self.tree.insert("", "end", values=(item["name"], item["amount"], item["unit"]))

    def save_recipe(self):
        prod_str = self.combo_product.get()
        if "請選擇" in prod_str or not prod_str:
            messagebox.showwarning("警告", "請先選擇一個產品")
            return

        prod_id = int(prod_str.split(" - ")[0])
        data_to_save = [(x["id"], x["amount"]) for x in self.current_ingredients]
        
        success, msg = save_recipe_to_db(prod_id, data_to_save)
        if success:
            messagebox.showinfo("成功", "配方已儲存！(僅供紀錄參考)")
        else:
            messagebox.showerror("失敗", msg)