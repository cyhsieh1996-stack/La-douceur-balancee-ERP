import customtkinter as ctk
from tkinter import ttk, messagebox
# 記得引入新函式 search_materials
from logic.raw_materials_logic import add_material, update_material, get_all_materials, delete_material, get_all_vendors, search_materials
from ui.theme import Color, Font, Layout

class RawMaterialsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_id = None

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(20, 20))
        self.create_form()

        # 搜尋與列表
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 10))
        self.create_search_bar() # 新增搜尋列

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()
        self.update_vendor_list()

    def create_form(self):
        # ... (保持原本的表單程式碼不變) ...
        # 為了節省篇幅，請保留您原本的 create_form 內容
        # 如果需要完整版請告訴我，目前假設您只覆蓋 create_search_bar 和 refresh_table 相關
        ctk.CTkLabel(self.form_card, text="原料資料維護", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=20, pady=(15, 5))
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=5)
        content.columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(content, text="原料名稱", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_name = ctk.CTkEntry(content); self.entry_name.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(content, text="類別", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.combo_category = ctk.CTkComboBox(content, values=["粉類", "糖類", "乳製品", "油類", "蛋類", "水果類", "堅果類", "包材", "其他"]); self.combo_category.set("粉類"); self.combo_category.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(content, text="廠牌", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_brand = ctk.CTkEntry(content); self.entry_brand.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(content, text="廠商", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        self.combo_vendor = ctk.CTkComboBox(content); self.combo_vendor.set(""); self.combo_vendor.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(content, text="庫存單位", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_unit = ctk.CTkComboBox(content, values=["kg", "g", "ml", "L", "罐", "包", "箱", "個"]); self.combo_unit.set("kg"); self.combo_unit.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(content, text="安全庫存量", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.entry_safe = ctk.CTkEntry(content, placeholder_text="0"); self.entry_safe.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        btn_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_frame.pack(anchor="e", padx=20, pady=(0, 20))
        self.btn_add = ctk.CTkButton(btn_frame, text="＋ 新增原料", fg_color=Color.PRIMARY, width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_add); self.btn_add.pack(side="left", padx=5)
        self.btn_update = ctk.CTkButton(btn_frame, text="儲存修改", fg_color="#2CC985", width=Layout.BTN_WIDTH, height=Layout.BTN_HEIGHT, command=self.handle_update)
        self.btn_delete = ctk.CTkButton(btn_frame, text="刪除", fg_color=Color.DANGER, width=100, height=Layout.BTN_HEIGHT, command=self.handle_delete)
        self.btn_cancel = ctk.CTkButton(btn_frame, text="取消", fg_color="transparent", text_color=Color.TEXT_DARK, width=80, height=Layout.BTN_HEIGHT, command=self.deselect_item)

    def create_search_bar(self):
        # 搜尋框與按鈕
        self.entry_search = ctk.CTkEntry(self.filter_frame, placeholder_text="搜尋名稱、廠牌或廠商...", width=300)
        self.entry_search.pack(side="left", padx=(0, 10))
        
        # 綁定 Enter 鍵
        self.entry_search.bind("<Return>", lambda e: self.handle_search())

        btn_search = ctk.CTkButton(self.filter_frame, text="🔍 搜尋", width=80, command=self.handle_search)
        btn_search.pack(side="left")
        
        btn_clear = ctk.CTkButton(self.filter_frame, text="重置", fg_color="transparent", text_color=Color.TEXT_DARK, width=60, command=self.clear_search)
        btn_clear.pack(side="left", padx=5)

    def create_table(self):
        columns = ("id", "name", "category", "brand", "vendor", "unit", "stock", "safe")
        headers = ["ID", "原料名稱", "類別", "廠牌", "廠商", "單位", "庫存", "安全量"]
        widths = [40, 200, 80, 100, 100, 50, 70, 70]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white")
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")

        # ⚠️ 設定斑馬紋顏色
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def refresh_table(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        # 如果有傳入 data (搜尋結果) 就用，否則撈全部
        rows = data if data is not None else get_all_materials()
        
        for i, row in enumerate(rows):
            values = (row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8])
            # ⚠️ 應用斑馬紋
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def handle_search(self):
        keyword = self.entry_search.get()
        if keyword:
            results = search_materials(keyword)
            self.refresh_table(results)
        else:
            self.refresh_table()

    def clear_search(self):
        self.entry_search.delete(0, "end")
        self.refresh_table()

    # ... (其餘 update_vendor_list, on_tree_select, deselect_item, handle_add, handle_update, handle_delete 保持不變) ...
    def update_vendor_list(self):
        vendors = get_all_vendors(); self.combo_vendor.configure(values=vendors)
    def on_tree_select(self, event):
        selected = self.tree.selection(); 
        if not selected: return
        val = self.tree.item(selected[0], "values"); self.selected_id = val[0]
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, val[1])
        self.combo_category.set(val[2]); self.entry_brand.delete(0, "end"); self.entry_brand.insert(0, val[3])
        self.combo_vendor.set(val[4]); self.combo_unit.set(val[5]); self.entry_safe.delete(0, "end"); self.entry_safe.insert(0, val[7])
        self.btn_add.pack_forget(); self.btn_cancel.pack(side="right", padx=5); self.btn_delete.pack(side="right", padx=5); self.btn_update.pack(side="right", padx=5)
    def deselect_item(self):
        self.selected_id = None; self.entry_name.delete(0, "end"); self.entry_brand.delete(0, "end"); self.combo_vendor.set(""); self.entry_safe.delete(0, "end")
        self.btn_update.pack_forget(); self.btn_delete.pack_forget(); self.btn_cancel.pack_forget(); self.btn_add.pack(side="left", padx=5)
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
    def handle_add(self):
        name = self.entry_name.get(); cat = self.combo_category.get(); brand = self.entry_brand.get(); vendor = self.combo_vendor.get(); unit = self.combo_unit.get(); safe_s = self.entry_safe.get()
        if not name: messagebox.showwarning("警告", "請填寫名稱"); return
        try: safe = float(safe_s) if safe_s else 0
        except: messagebox.showerror("錯誤", "數值格式錯誤"); return
        success, msg = add_material(name, cat, brand, vendor, unit, safe)
        if success: self.deselect_item(); self.refresh_table(); self.update_vendor_list()
        else: messagebox.showerror("失敗", msg)
    def handle_update(self):
        if not self.selected_id: return
        name = self.entry_name.get(); cat = self.combo_category.get(); brand = self.entry_brand.get(); vendor = self.combo_vendor.get(); unit = self.combo_unit.get(); safe_s = self.entry_safe.get()
        if not name: messagebox.showwarning("警告", "請填寫名稱"); return
        try: safe = float(safe_s) if safe_s else 0
        except: messagebox.showerror("錯誤", "數值格式錯誤"); return
        success, msg = update_material(self.selected_id, name, cat, brand, vendor, unit, safe)
        if success: messagebox.showinfo("成功", "資料已更新"); self.deselect_item(); self.refresh_table(); self.update_vendor_list()
        else: messagebox.showerror("失敗", msg)
    def handle_delete(self):
        if not self.selected_id: return
        if messagebox.askyesno("刪除", f"確定要刪除此原料嗎？\n(ID: {self.selected_id})"):
            success, msg = delete_material(self.selected_id); 
            if success: self.deselect_item(); self.refresh_table(); self.update_vendor_list()
            else: messagebox.showerror("失敗", msg)