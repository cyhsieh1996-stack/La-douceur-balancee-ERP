import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.products_logic import (
    add_product, 
    update_product,
    get_all_products, 
    delete_product, 
    get_unique_product_categories, 
    get_products_by_category
)
from ui.theme import Color, Font

class ProductsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.selected_id = None

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="產品基本資料 Products Master Data", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 輸入區
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))
        self.create_form()

        # 3. 篩選
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 10))
        self.create_filter_bar()

        # 4. 列表
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()
        self.refresh_filter_options()

    def create_form(self):
        self.form_card.columnconfigure((0, 1, 2, 3), weight=1)
        
        # 名稱
        ctk.CTkLabel(self.form_card, text="產品名稱", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_name = ctk.CTkEntry(self.form_card, placeholder_text="例如：草莓蛋糕")
        self.entry_name.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # 類別
        ctk.CTkLabel(self.form_card, text="產品類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")
        self.combo_category = ctk.CTkComboBox(
            self.form_card, 
            values=["切片蛋糕", "整模蛋糕", "常溫餅乾", "常溫蛋糕/塔", "飲品", "禮盒", "其他"],
        )
        self.combo_category.set("切片蛋糕")
        self.combo_category.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")

        # 售價
        ctk.CTkLabel(self.form_card, text="售價 (元)", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=20, pady=(20, 5), sticky="w")
        self.entry_price = ctk.CTkEntry(self.form_card, placeholder_text="輸入整數金額")
        self.entry_price.grid(row=1, column=2, padx=20, pady=(0, 20), sticky="ew")

        # 保存期限 (標示為選填)
        ctk.CTkLabel(self.form_card, text="保存期限(天) [選填]", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=3, padx=20, pady=(20, 5), sticky="w")
        self.entry_life = ctk.CTkEntry(self.form_card, placeholder_text="自產商品請填天數")
        self.entry_life.grid(row=1, column=3, padx=20, pady=(0, 20), sticky="ew")

        # 按鈕區
        self.btn_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, columnspan=4, padx=20, pady=(0, 20), sticky="ew")
        
        self.btn_add = ctk.CTkButton(self.btn_frame, text="＋ 新增產品", fg_color=Color.PRIMARY, height=40, command=self.handle_add)
        self.btn_add.pack(fill="x")

        self.btn_update = ctk.CTkButton(self.btn_frame, text="儲存修改", fg_color="#2CC985", height=40, command=self.handle_update)
        self.btn_delete = ctk.CTkButton(self.btn_frame, text="刪除", fg_color=Color.DANGER, height=40, width=100, command=self.handle_delete)
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="取消", fg_color="transparent", text_color=Color.TEXT_DARK, height=40, width=80, command=self.deselect_item)

    def create_filter_bar(self):
        ctk.CTkLabel(self.filter_frame, text="🔍 類別篩選：", font=Font.BODY, text_color=Color.TEXT_DARK).pack(side="left", padx=(0, 10))
        self.combo_filter = ctk.CTkComboBox(self.filter_frame, state="readonly", width=200, command=self.handle_filter_change)
        self.combo_filter.set("顯示全部")
        self.combo_filter.pack(side="left")
        ctk.CTkButton(self.filter_frame, text="顯示全部", fg_color="transparent", border_width=1, border_color="#999999", text_color=Color.TEXT_DARK, width=80, command=lambda: self.handle_filter_change("顯示全部")).pack(side="left", padx=10)

    def create_table(self):
        columns = ("id", "name", "category", "price", "life")
        headers = ["ID", "產品名稱", "類別", "售價", "保存天數"]
        widths = [50, 300, 150, 100, 100]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, fieldbackground="white", font=Font.SMALL)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items: return

        item_values = self.tree.item(selected_items[0], "values")
        self.selected_id = item_values[0]
        
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, item_values[1])
        
        self.combo_category.set(item_values[2])
        
        self.entry_price.delete(0, "end")
        self.entry_price.insert(0, item_values[3])
        
        self.entry_life.delete(0, "end")
        # 如果是 None 或空字串，就不填入
        if item_values[4] and item_values[4] != "None":
            self.entry_life.insert(0, item_values[4])

        self.btn_add.pack_forget()
        self.btn_cancel.pack(side="right", padx=5)
        self.btn_delete.pack(side="right", padx=5)
        self.btn_update.pack(side="right", padx=5)

    def deselect_item(self):
        self.selected_id = None
        self.clear_form()
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()
        self.btn_cancel.pack_forget()
        self.btn_add.pack(fill="x")

    def handle_add(self):
        name = self.entry_name.get()
        category = self.combo_category.get()
        price_str = self.entry_price.get()
        life_str = self.entry_life.get()

        if not name or not price_str:
            messagebox.showwarning("欄位未填", "請填寫名稱與售價")
            return

        try:
            price = int(float(price_str))
            # 如果欄位是空的，就設為 None
            life = int(life_str) if life_str.strip() else None
        except ValueError:
            messagebox.showerror("格式錯誤", "售價與天數必須是數字")
            return

        success, msg = add_product(name, category, price, life)
        if success:
            self.clear_form()
            self.refresh_table()
            self.refresh_filter_options()
        else:
            messagebox.showerror("錯誤", msg)

    def handle_update(self):
        if not self.selected_id: return
        name = self.entry_name.get()
        category = self.combo_category.get()
        price_str = self.entry_price.get()
        life_str = self.entry_life.get()

        if not name or not price_str:
            messagebox.showwarning("欄位未填", "請填寫名稱與售價")
            return

        try:
            price = int(float(price_str))
            life = int(life_str) if life_str.strip() else None
        except ValueError:
            messagebox.showerror("格式錯誤", "售價與天數必須是數字")
            return

        success, msg = update_product(self.selected_id, name, category, price, life)
        if success:
            messagebox.showinfo("成功", "資料已更新")
            self.deselect_item()
            self.refresh_table()
            self.refresh_filter_options()
        else:
            messagebox.showerror("錯誤", msg)

    def handle_delete(self):
        if not self.selected_id: return
        confirm = messagebox.askyesno("確認刪除", f"確定要刪除這個產品嗎？\n(ID: {self.selected_id})")
        if confirm:
            success, msg = delete_product(self.selected_id)
            if success:
                self.deselect_item()
                self.refresh_table()
                self.refresh_filter_options()
            else:
                messagebox.showerror("錯誤", msg)

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_price.delete(0, "end")
        self.entry_life.delete(0, "end")

    def refresh_filter_options(self):
        categories = get_unique_product_categories()
        options = ["顯示全部"] + categories
        self.combo_filter.configure(values=options)

    def handle_filter_change(self, choice):
        self.deselect_item()
        if choice == "顯示全部":
            self.combo_filter.set("顯示全部")
            self.refresh_table(filter_category=None)
        else:
            self.refresh_table(filter_category=choice)

    def refresh_table(self, filter_category=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if filter_category:
            rows = get_products_by_category(filter_category)
        else:
            rows = get_all_products()

        for row in rows:
            try:
                price_display = int(row['price'])
            except:
                price_display = 0
            
            # 如果是 None，顯示空白
            life_display = row['shelf_life'] if row['shelf_life'] is not None else ""
            
            values = (row['id'], row['name'], row['category'], price_display, life_display)
            self.tree.insert("", "end", values=values)