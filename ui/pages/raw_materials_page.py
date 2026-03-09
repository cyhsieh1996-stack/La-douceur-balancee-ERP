import customtkinter as ctk
from tkinter import ttk, messagebox
from logic.raw_materials_logic import add_material, update_material, get_all_materials, delete_material, get_all_vendors, search_materials
from ui.theme import Color, Font, Layout
from ui.input_utils import clean_text, parse_non_negative_float

class RawMaterialsPage(ctk.CTkFrame):
    LAST_CATEGORY = "粉類"
    LAST_UNIT = "kg"
    LAST_VENDOR = ""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_id = None

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.form_card.pack(fill="x", pady=(10, 10)) 
        self.create_form()

        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 5))
        self.create_search_bar()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()
        self.update_vendor_list()
        self.bind_submit_shortcuts()
        self.entry_name.focus_set()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="原料資料維護", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(10, 5))
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, 10))
        content.columnconfigure((0, 1, 2, 3), weight=1)

        def create_field(parent, label_text, row, col):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: frame.grid_configure(padx=(0, 0))
            ctk.CTkLabel(frame, text=label_text, font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
            entry = ctk.CTkEntry(frame, height=Layout.BTN_HEIGHT)
            entry.pack(fill="x")
            return entry

        def create_combo(parent, label_text, values, row, col):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=row, column=col, padx=(0, Layout.GRID_GAP_X), pady=(0, Layout.GRID_GAP_Y), sticky="ew")
            if col == 3: frame.grid_configure(padx=(0, 0))
            ctk.CTkLabel(frame, text=label_text, font=Font.BODY, text_color=Color.TEXT_DARK, height=20).pack(anchor="w", pady=(0, 2))
            combo = ctk.CTkComboBox(frame, values=values, height=Layout.BTN_HEIGHT, state="readonly")
            combo.pack(fill="x")
            return combo

        # Row 0
        self.entry_name = create_field(content, "原料名稱", 0, 0)
        self.combo_category = create_combo(content, "類別", ["粉類", "糖類", "乳製品", "油類", "蛋類", "水果類", "堅果類", "包材", "其他"], 0, 1)
        self.combo_category.set(self.LAST_CATEGORY)
        self.entry_brand = create_field(content, "廠牌", 0, 2)
        self.combo_vendor = create_combo(content, "廠商", [], 0, 3)
        self.combo_vendor.configure(state="normal")

        # Row 1
        self.combo_unit = create_combo(content, "庫存單位", ["kg", "g", "ml", "L", "罐", "包", "箱", "個"], 1, 0)
        self.combo_unit.set(self.LAST_UNIT)
        self.entry_safe = create_field(content, "安全庫存量", 1, 1)

        # Btn Row
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=4, pady=(5, 0), sticky="e")

        self.btn_add = ctk.CTkButton(btn_row, text="＋ 新增原料", fg_color=Color.PRIMARY, width=120, height=Layout.BTN_HEIGHT, command=self.handle_add)
        self.btn_add.pack(side="right")

        self.edit_btn_group = ctk.CTkFrame(btn_row, fg_color="transparent")
        self.btn_cancel = ctk.CTkButton(self.edit_btn_group, text="取消", fg_color=Color.GRAY_BUTTON, hover_color=Color.GRAY_BUTTON_HOVER, text_color=Color.TEXT_DARK, width=80, height=Layout.BTN_HEIGHT, command=self.deselect_item)
        self.btn_cancel.pack(side="right", padx=(10, 0))
        self.btn_delete = ctk.CTkButton(self.edit_btn_group, text="刪除", fg_color=Color.DANGER, width=80, height=Layout.BTN_HEIGHT, command=self.handle_delete)
        self.btn_delete.pack(side="right", padx=(10, 0))
        self.btn_update = ctk.CTkButton(self.edit_btn_group, text="儲存修改", fg_color=Color.SUCCESS, width=120, height=Layout.BTN_HEIGHT, command=self.handle_update)
        self.btn_update.pack(side="right")

    def create_search_bar(self):
        container = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        container.pack(fill="x", padx=0) 
        self.entry_search = ctk.CTkEntry(container, placeholder_text="🔍 搜尋名稱、廠牌...", width=250, height=Layout.BTN_HEIGHT)
        self.entry_search.pack(side="left", padx=(0, 10)) 
        self.entry_search.bind("<Return>", lambda e: self.handle_search())
        ctk.CTkButton(container, text="搜尋", width=70, height=Layout.BTN_HEIGHT, command=self.handle_search).pack(side="left")
        ctk.CTkButton(container, text="重置", fg_color=Color.GRAY_BUTTON, text_color=Color.TEXT_DARK, hover_color=Color.GRAY_BUTTON_HOVER, width=60, height=Layout.BTN_HEIGHT, command=self.clear_search).pack(side="left", padx=10)
        ctk.CTkButton(container, text="批次貼上", fg_color=Color.INFO, width=90, height=Layout.BTN_HEIGHT, command=self.open_bulk_paste_dialog).pack(side="left", padx=(10, 0))

    def bind_submit_shortcuts(self):
        self.entry_name.bind("<Return>", lambda _e: self.entry_brand.focus_set())
        self.entry_brand.bind("<Return>", lambda _e: self.combo_vendor.focus_set())
        self.combo_vendor.bind("<Return>", lambda _e: self.entry_safe.focus_set())
        self.entry_safe.bind("<Return>", lambda _e: self.handle_update() if self.selected_id else self.handle_add())

    def open_bulk_paste_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("批次貼上原料")
        dialog.geometry("780x520")
        dialog.lift()

        ctk.CTkLabel(
            dialog,
            text="每行一筆：名稱,類別,廠牌,廠商,單位,安全庫存量",
            font=Font.BODY,
            text_color=Color.TEXT_DARK,
        ).pack(anchor="w", padx=16, pady=(12, 6))
        ctk.CTkLabel(
            dialog,
            text="也支援 Tab 分隔；未填欄位將套用目前表單預設值。",
            font=Font.SMALL,
            text_color=Color.TEXT_LIGHT,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        textbox = ctk.CTkTextbox(dialog)
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        button_row = ctk.CTkFrame(dialog, fg_color="transparent")
        button_row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(
            button_row,
            text="預覽",
            width=90,
            fg_color=Color.GRAY_BUTTON,
            text_color=Color.TEXT_DARK,
            hover_color=Color.GRAY_BUTTON_HOVER,
            command=lambda: self.preview_bulk_paste(textbox.get("1.0", "end")),
        ).pack(side="right", padx=(0, 10))
        ctk.CTkButton(
            button_row,
            text="開始匯入",
            width=120,
            command=lambda: self.handle_bulk_paste(textbox.get("1.0", "end"), dialog),
        ).pack(side="right")

    def parse_bulk_paste_lines(self, raw_text):
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        default_category = clean_text(self.combo_category.get()) or "其他"
        default_unit = clean_text(self.combo_unit.get()) or "kg"
        default_vendor = clean_text(self.combo_vendor.get())
        parsed_rows = []
        errors = []

        for idx, line in enumerate(lines, start=1):
            parts = [p.strip() for p in (line.split("\t") if "\t" in line else line.split(","))]
            name = clean_text(parts[0]) if len(parts) >= 1 else ""
            category = clean_text(parts[1]) if len(parts) >= 2 and clean_text(parts[1]) else default_category
            brand = clean_text(parts[2]) if len(parts) >= 3 else ""
            vendor = clean_text(parts[3]) if len(parts) >= 4 and clean_text(parts[3]) else default_vendor
            unit = clean_text(parts[4]) if len(parts) >= 5 and clean_text(parts[4]) else default_unit
            safe_raw = parts[5] if len(parts) >= 6 else "0"

            if not name:
                errors.append(f"第 {idx} 行：原料名稱空白")
                continue
            safe_stock, err = parse_non_negative_float(safe_raw, "安全庫存量")
            if err:
                errors.append(f"第 {idx} 行：{err}")
                continue

            parsed_rows.append((idx, name, category, brand, vendor, unit, safe_stock))

        return lines, parsed_rows, errors

    def preview_bulk_paste(self, raw_text):
        lines, parsed_rows, errors = self.parse_bulk_paste_lines(raw_text)
        if not lines:
            messagebox.showwarning("警告", "沒有可預覽的資料")
            return
        summary = f"總行數 {len(lines)}，可匯入 {len(parsed_rows)}，有誤 {len(errors)}"
        if errors:
            summary += "\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                summary += f"\n...其餘 {len(errors)-10} 筆錯誤省略"
        messagebox.showinfo("批次預覽", summary)

    def handle_bulk_paste(self, raw_text, dialog):
        lines, parsed_rows, errors = self.parse_bulk_paste_lines(raw_text)
        if not lines:
            messagebox.showwarning("警告", "沒有可匯入的資料")
            return

        ok_count = 0
        fail_count = len(errors)
        for idx, name, category, brand, vendor, unit, safe_stock in parsed_rows:
            success, msg = add_material(name, category, brand, vendor, unit, safe_stock)
            if success:
                ok_count += 1
                self.__class__.LAST_CATEGORY = category or self.__class__.LAST_CATEGORY
                self.__class__.LAST_UNIT = unit or self.__class__.LAST_UNIT
                self.__class__.LAST_VENDOR = vendor
            else:
                fail_count += 1
                errors.append(f"第 {idx} 行：{msg}")

        self.refresh_table()
        self.update_vendor_list()
        self.combo_category.set(self.__class__.LAST_CATEGORY)
        self.combo_unit.set(self.__class__.LAST_UNIT)
        self.combo_vendor.set(self.__class__.LAST_VENDOR)
        summary = f"成功 {ok_count} 筆，失敗 {fail_count} 筆"
        if errors:
            summary += "\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                summary += f"\n...其餘 {len(errors)-10} 筆錯誤省略"
        messagebox.showinfo("批次匯入結果", summary)
        dialog.destroy()

    def create_table(self):
        columns = ("id", "name", "category", "brand", "vendor", "unit", "stock", "safe")
        headers = ["ID", "原料名稱", "類別", "廠牌", "廠商", "單位", "庫存", "安全量"]
        widths = [40, 180, 80, 100, 100, 60, 80, 80]
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths): self.tree.heading(col, text=h); self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure('odd', background='white'); self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        scroll_y = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview); scroll_x = ttk.Scrollbar(self.table_card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5); scroll_x.pack(side="bottom", fill="x", padx=5, pady=(0, 5))
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def refresh_table(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = data if data is not None else get_all_materials()
        for i, row in enumerate(rows):
            # ⚠️ 智慧修整：庫存與安全量
            try:
                raw_stock = float(row[7])
                stock_val = int(raw_stock) if raw_stock.is_integer() else round(raw_stock, 3)
            except: stock_val = 0
            
            try:
                raw_safe = float(row[8])
                safe_val = int(raw_safe) if raw_safe.is_integer() else round(raw_safe, 3)
            except: safe_val = 0

            values = (row[0], row[1], row[2], row[3], row[4], row[5], stock_val, safe_val)
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def handle_search(self):
        keyword = self.entry_search.get()
        if keyword: results = search_materials(keyword); self.refresh_table(results)
        else: self.refresh_table()
    def clear_search(self): self.entry_search.delete(0, "end"); self.refresh_table()
    def update_vendor_list(self):
        vendors = get_all_vendors()
        self.combo_vendor.configure(values=vendors)
        if self.LAST_VENDOR:
            self.combo_vendor.set(self.LAST_VENDOR)
    def on_tree_select(self, event):
        selected = self.tree.selection(); 
        if not selected: return
        val = self.tree.item(selected[0], "values"); self.selected_id = val[0]
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, val[1]); self.combo_category.set(val[2]); self.entry_brand.delete(0, "end"); self.entry_brand.insert(0, val[3]); self.combo_vendor.set(val[4]); self.combo_unit.set(val[5]); 
        
        # 編輯時也要顯示整數 (如果可以)
        self.entry_safe.delete(0, "end")
        try:
            safe_v = float(val[7])
            self.entry_safe.insert(0, str(int(safe_v)) if safe_v.is_integer() else str(safe_v))
        except: self.entry_safe.insert(0, val[7])

        self.btn_add.pack_forget(); self.edit_btn_group.pack(side="right")
    def on_tree_double_click(self, _event):
        self.on_tree_select(None)
        self.entry_name.focus_set()
    def deselect_item(self):
        self.selected_id = None; self.entry_name.delete(0, "end"); self.entry_brand.delete(0, "end"); self.combo_vendor.set(""); self.entry_safe.delete(0, "end")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        self.edit_btn_group.pack_forget(); self.btn_add.pack(side="right")
    def handle_add(self):
        name = clean_text(self.entry_name.get()); cat = clean_text(self.combo_category.get()); brand = clean_text(self.entry_brand.get()); vendor = clean_text(self.combo_vendor.get()); unit = clean_text(self.combo_unit.get()); safe_s = self.entry_safe.get()
        if not name: messagebox.showwarning("警告", "請填寫名稱"); return
        safe, err = parse_non_negative_float(safe_s, "安全庫存量")
        if err: messagebox.showerror("錯誤", err); return
        success, msg = add_material(name, cat, brand, vendor, unit, safe)
        if success:
            self.__class__.LAST_CATEGORY = cat or self.__class__.LAST_CATEGORY
            self.__class__.LAST_UNIT = unit or self.__class__.LAST_UNIT
            self.__class__.LAST_VENDOR = vendor
            self.deselect_item(); self.refresh_table(); self.update_vendor_list()
            self.combo_category.set(self.__class__.LAST_CATEGORY); self.combo_unit.set(self.__class__.LAST_UNIT); self.combo_vendor.set(self.__class__.LAST_VENDOR); self.entry_name.focus_set()
        else: messagebox.showerror("失敗", msg)
    def handle_update(self):
        if not self.selected_id: return
        name = clean_text(self.entry_name.get()); cat = clean_text(self.combo_category.get()); brand = clean_text(self.entry_brand.get()); vendor = clean_text(self.combo_vendor.get()); unit = clean_text(self.combo_unit.get()); safe_s = self.entry_safe.get()
        if not name: messagebox.showwarning("警告", "請填寫名稱"); return
        safe, err = parse_non_negative_float(safe_s, "安全庫存量")
        if err: messagebox.showerror("錯誤", err); return
        success, msg = update_material(self.selected_id, name, cat, brand, vendor, unit, safe)
        if success:
            self.__class__.LAST_CATEGORY = cat or self.__class__.LAST_CATEGORY
            self.__class__.LAST_UNIT = unit or self.__class__.LAST_UNIT
            self.__class__.LAST_VENDOR = vendor
            messagebox.showinfo("成功", "資料已更新"); self.deselect_item(); self.refresh_table(); self.update_vendor_list()
            self.combo_category.set(self.__class__.LAST_CATEGORY); self.combo_unit.set(self.__class__.LAST_UNIT); self.combo_vendor.set(self.__class__.LAST_VENDOR); self.entry_name.focus_set()
        else: messagebox.showerror("失敗", msg)
    def handle_delete(self):
        if not self.selected_id: return
        if messagebox.askyesno("刪除", f"確定要刪除此原料嗎？\n(ID: {self.selected_id})"):
            success, msg = delete_material(self.selected_id); 
            if success: self.deselect_item(); self.refresh_table(); self.update_vendor_list()
            else: messagebox.showerror("失敗", msg)
