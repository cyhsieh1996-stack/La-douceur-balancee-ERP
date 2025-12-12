import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.raw_materials_logic import add_material, get_all_materials, delete_material
from ui.theme import Color, Font, Layout

class RawMaterialsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 輸入區塊
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 20))
        self.create_form()

        # 2. 列表區塊
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="新增原料", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2, 3), weight=1)
        
        # 第一排
        ctk.CTkLabel(content, text="原料名稱", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_name = ctk.CTkEntry(content)
        self.entry_name.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.combo_category = ctk.CTkComboBox(content, values=["粉類", "糖類", "乳製品", "油類", "蛋類", "水果類", "堅果類", "包材", "其他"])
        self.combo_category.set("粉類")
        self.combo_category.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="廠牌", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_brand = ctk.CTkEntry(content)
        self.entry_brand.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="廠商", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        self.entry_vendor = ctk.CTkEntry(content)
        self.entry_vendor.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")

        # 第二排
        ctk.CTkLabel(content, text="庫存單位", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_unit = ctk.CTkComboBox(content, values=["kg", "g", "ml", "L", "罐", "包", "箱", "個"])
        self.combo_unit.set("kg")
        self.combo_unit.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="進貨單價", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.entry_price = ctk.CTkEntry(content, placeholder_text="0")
        self.entry_price.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(content, text="安全庫存量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.entry_safe = ctk.CTkEntry(content, placeholder_text="0")
        self.entry_safe.grid(row=3, column=2, padx=10, pady=(0, 10), sticky="ew")

        # 按鈕區 (放在第二排的第四格位置，或者獨立一行)
        self.btn_add = ctk.CTkButton(content, text="＋ 新增原料", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_add)
        self.btn_add.grid(row=3, column=3, padx=10, pady=(0, 10), sticky="e") # sticky="e" 靠右

    def create_table(self):
        columns = ("id", "name", "category", "brand", "vendor", "unit", "price", "stock", "safe")
        headers = ["ID", "原料名稱", "類別", "廠牌", "廠商", "單位", "單價", "庫存", "安全量"]
        widths = [40, 150, 80, 100, 100, 60, 60, 80, 80]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white")
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_double_click_delete)

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_all_materials()
        for row in rows:
            values = list(row)
            self.tree.insert("", "end", values=values)

    def handle_add(self):
        name = self.entry_name.get(); cat = self.combo_category.get(); brand = self.entry_brand.get(); vendor = self.entry_vendor.get(); unit = self.combo_unit.get(); price_s = self.entry_price.get(); safe_s = self.entry_safe.get()
        if not name: messagebox.showwarning("警告", "請填寫名稱"); return
        try: price = float(price_s) if price_s else 0; safe = float(safe_s) if safe_s else 0
        except: messagebox.showerror("錯誤", "數值格式錯誤"); return
        success, msg = add_material(name, cat, brand, vendor, unit, price, safe)
        if success:
            self.entry_name.delete(0, "end"); self.entry_brand.delete(0, "end"); self.entry_vendor.delete(0, "end"); self.entry_price.delete(0, "end"); self.entry_safe.delete(0, "end")
            self.refresh_table()
        else: messagebox.showerror("失敗", msg)

    def on_double_click_delete(self, event):
        selected = self.tree.selection()
        if not selected: return
        val = self.tree.item(selected[0], "values")
        mat_id = val[0]
        if messagebox.askyesno("刪除", f"確定要刪除 {val[1]} 嗎？"):
            success, msg = delete_material(mat_id)
            if success: self.refresh_table()
            else: messagebox.showerror("失敗", msg)