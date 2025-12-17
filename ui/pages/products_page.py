import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.products_logic import (
    add_product, update_product, get_all_products, delete_product, 
    get_unique_product_categories, get_products_by_category, search_products
)
from ui.theme import Color, Font, Layout

class ProductsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_id = None

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 15))
        self.create_form()

        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 10))
        self.create_filter_bar()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()
        self.refresh_filter_options()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="產品資料維護", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(Layout.CARD_PADDING, 10))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, Layout.CARD_PADDING))
        content.columnconfigure((0, 1, 2, 3), weight=1)

        def create_field(parent, label_text, row, col):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: frame.grid_configure(padx=(0, 0))
            ctk.CTkLabel(frame, text=label_text, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            entry = ctk.CTkEntry(frame, height=35)
            entry.pack(fill="x")
            return entry

        def create_combo(parent, label_text, values, row, col):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: frame.grid_configure(padx=(0, 0))
            ctk.CTkLabel(frame, text=label_text, font=Font.BODY, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 5))
            combo = ctk.CTkComboBox(frame, values=values, height=35)
            combo.pack(fill="x")
            return combo

        # Row 0
        self.entry_name = create_field(content, "產品名稱", 0, 0)
        self.combo_category = create_combo(content, "類別", ["切片蛋糕", "整模蛋糕", "常溫餅乾", "常溫蛋糕/塔", "飲品", "禮盒", "其他"], 0, 1)
        self.entry_price = create_field(content, "售價 (元)", 0, 2)
        self.entry_cost = create_field(content, "成本 (元)", 0, 3)

        # Row 1
        self.entry_life = create_field(content, "保存期限 (天)", 1, 0)
        # 1-1, 1-2, 1-3 空白

        # 按鈕區 (Row 2)
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=4, pady=(10, 0), sticky="e")

        self.btn_add = ctk.CTkButton(btn_row, text="＋ 新增產品", fg_color=Color.PRIMARY, width=140, height=38, command=self.handle_add)
        self.btn_add.pack(side="right")

        self.edit_btn_group = ctk.CTkFrame(btn_row, fg_color="transparent")
        self.btn_cancel = ctk.CTkButton(self.edit_btn_group, text="取消", fg_color=Color.GRAY_BUTTON, hover_color=Color.GRAY_BUTTON_HOVER, text_color=Color.TEXT_DARK, width=80, height=38, command=self.deselect_item)
        self.btn_cancel.pack(side="right", padx=(10, 0))
        self.btn_delete = ctk.CTkButton(self.edit_btn_group, text="刪除", fg_color=Color.DANGER, width=80, height=38, command=self.handle_delete)
        self.btn_delete.pack(side="right", padx=(10, 0))
        self.btn_update = ctk.CTkButton(self.edit_btn_group, text="儲存修改", fg_color=Color.SUCCESS, width=140, height=38, command=self.handle_update)
        self.btn_update.pack(side="right")

    def create_filter_bar(self):
        container = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        container.pack(fill="x", padx=0) 

        self.entry_search = ctk.CTkEntry(container, placeholder_text="🔍 搜尋產品名稱...", width=280, height=35)
        self.entry_search.pack(side="left", padx=(0, 10)) 
        self.entry_search.bind("<Return>", lambda e: self.handle_search())
        ctk.CTkButton(container, text="搜尋", width=80, height=35, command=self.handle_search).pack(side="left")

        ctk.CTkLabel(container, text="類別篩選：", font=Font.BODY, text_color=Color.TEXT_DARK).pack(side="left", padx=(30, 10))
        self.combo_filter = ctk.CTkComboBox(container, state="readonly", width=160, height=35, command=self.handle_filter_change)
        self.combo_filter.set("顯示全部")
        self.combo_filter.pack(side="left")
        
        ctk.CTkButton(container, text="重置", fg_color=Color.GRAY_BUTTON, text_color=Color.TEXT_DARK, hover_color=Color.GRAY_BUTTON_HOVER, width=70, height=35, command=self.reset_filters).pack(side="left", padx=10)

    def create_table(self):
        columns = ("id", "name", "category", "price", "cost", "life", "stock")
        headers = ["ID", "產品名稱", "類別", "售價", "成本", "保存天數", "目前庫存"]
        widths = [40, 200, 120, 80, 80, 80, 80]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, fieldbackground="white", font=Font.SMALL)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths): self.tree.heading(col, text=h); self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        
        scroll_y = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(self.table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)
        scroll_x.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def refresh_table(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        if data is not None: rows = data
        else:
            filter_cat = self.combo_filter.get()
            rows = get_all_products() if filter_cat == "顯示全部" else get_products_by_category(filter_cat)
        for i, row in enumerate(rows):
            try: price = int(row[3])
            except: price = 0
            try: cost = int(row[4])
            except: cost = 0
            try: stock = int(row[6])
            except: stock = 0
            life = row[5] if row[5] is not None else ""
            values = (row[0], row[1], row[2], price, cost, life, stock)
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def handle_search(self):
        kw = self.entry_search.get()
        if kw: self.combo_filter.set("顯示全部"); self.refresh_table(search_products(kw))
        else: self.refresh_table()
    def reset_filters(self): self.entry_search.delete(0, "end"); self.combo_filter.set("顯示全部"); self.refresh_table()
    def handle_filter_change(self, choice): self.entry_search.delete(0, "end"); self.deselect_item(); self.refresh_table()
    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0], "values"); self.selected_id = val[0]
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, val[1])
        self.combo_category.set(val[2])
        self.entry_price.delete(0, "end"); self.entry_price.insert(0, val[3])
        self.entry_cost.delete(0, "end"); self.entry_cost.insert(0, val[4])
        self.entry_life.delete(0, "end"); 
        if val[5] and val[5] != "None": self.entry_life.insert(0, val[5])
        self.btn_add.pack_forget(); self.edit_btn_group.pack(side="right")
    def deselect_item(self):
        self.selected_id = None; self.clear_form()
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        self.edit_btn_group.pack_forget(); self.btn_add.pack(side="right")
    def handle_add(self):
        name = self.entry_name.get(); cat = self.combo_category.get(); p_str = self.entry_price.get(); c_str = self.entry_cost.get(); l_str = self.entry_life.get()
        if not name or not p_str: messagebox.showwarning("欄位未填", "請填寫名稱與售價"); return
        try: p = int(float(p_str)); c = int(float(c_str)) if c_str else 0; l = int(l_str) if l_str.strip() else None
        except: messagebox.showerror("格式錯誤", "金額必須是數字"); return
        success, msg = add_product(name, cat, p, c, l)
        if success: self.clear_form(); self.refresh_table(); self.refresh_filter_options()
        else: messagebox.showerror("錯誤", msg)
    def handle_update(self):
        if not self.selected_id: return
        name = self.entry_name.get(); cat = self.combo_category.get(); p_str = self.entry_price.get(); c_str = self.entry_cost.get(); l_str = self.entry_life.get()
        if not name or not p_str: messagebox.showwarning("欄位未填", "請填寫名稱與售價"); return
        try: p = int(float(p_str)); c = int(float(c_str)) if c_str else 0; l = int(l_str) if l_str.strip() else None
        except: messagebox.showerror("格式錯誤", "金額必須是數字"); return
        success, msg = update_product(self.selected_id, name, cat, p, c, l)
        if success: messagebox.showinfo("成功", "已更新"); self.deselect_item(); self.refresh_table(); self.refresh_filter_options()
        else: messagebox.showerror("錯誤", msg)
    def handle_delete(self):
        if not self.selected_id: return
        if messagebox.askyesno("確認", f"刪除 ID: {self.selected_id}?"):
            success, msg = delete_product(self.selected_id)
            if success: self.deselect_item(); self.refresh_table(); self.refresh_filter_options()
            else: messagebox.showerror("錯誤", msg)
    def clear_form(self):
        self.entry_name.delete(0, "end"); self.entry_price.delete(0, "end"); self.entry_cost.delete(0, "end"); self.entry_life.delete(0, "end")
    def refresh_filter_options(self):
        cats = get_unique_product_categories(); options = ["顯示全部"] + cats; self.combo_filter.configure(values=options)