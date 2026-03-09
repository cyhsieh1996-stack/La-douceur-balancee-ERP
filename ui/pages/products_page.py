import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from logic.products_logic import (
    add_product, update_product, get_all_products, delete_product, 
    get_unique_product_categories, get_products_by_category, search_products
)
from ui.theme import Color, Font, Layout
from ui.input_utils import clean_text, parse_non_negative_float, parse_optional_non_negative_int

class ProductsPage(ctk.CTkFrame):
    LAST_CATEGORY = "切片蛋糕"

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_id = None

        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.form_card.pack(fill="x", pady=(10, 10))
        self.create_form()

        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 5))
        self.create_filter_bar()

        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()
        self.refresh_filter_options()
        self.bind_submit_shortcuts()
        self.entry_name.focus_set()

    def create_form(self):
        ctk.CTkLabel(self.form_card, text="產品資料維護", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(10, 5))
        
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
        self.entry_name = create_field(content, "產品名稱", 0, 0)
        self.combo_category = create_combo(content, "類別", ["切片蛋糕", "整模蛋糕", "常溫餅乾", "常溫蛋糕/塔", "飲品", "禮盒", "其他"], 0, 1)
        self.combo_category.set(self.LAST_CATEGORY)
        self.entry_price = create_field(content, "售價 (元)", 0, 2)
        self.entry_cost = create_field(content, "成本 (元)", 0, 3)

        # Row 1
        self.entry_life = create_field(content, "保存期限 (天)", 1, 0)

        # 按鈕區 (Row 1, spanning right)
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.grid(row=1, column=1, columnspan=3, pady=(23, 0), sticky="e") # pady align with input

        self.btn_add = ctk.CTkButton(btn_row, text="＋ 新增產品", fg_color=Color.PRIMARY, width=120, height=Layout.BTN_HEIGHT, command=self.handle_add)
        self.btn_add.pack(side="right")

        self.edit_btn_group = ctk.CTkFrame(btn_row, fg_color="transparent")
        self.btn_cancel = ctk.CTkButton(self.edit_btn_group, text="取消", fg_color=Color.GRAY_BUTTON, hover_color=Color.GRAY_BUTTON_HOVER, text_color=Color.TEXT_DARK, width=80, height=Layout.BTN_HEIGHT, command=self.deselect_item)
        self.btn_cancel.pack(side="right", padx=(10, 0))
        self.btn_delete = ctk.CTkButton(self.edit_btn_group, text="刪除", fg_color=Color.DANGER, width=80, height=Layout.BTN_HEIGHT, command=self.handle_delete)
        self.btn_delete.pack(side="right", padx=(10, 0))
        self.btn_update = ctk.CTkButton(self.edit_btn_group, text="儲存修改", fg_color=Color.SUCCESS, width=120, height=Layout.BTN_HEIGHT, command=self.handle_update)
        self.btn_update.pack(side="right")

    def create_filter_bar(self):
        container = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        container.pack(fill="x", padx=0) 

        self.entry_search = ctk.CTkEntry(container, placeholder_text="🔍 搜尋產品名稱...", width=250, height=Layout.BTN_HEIGHT)
        self.entry_search.pack(side="left", padx=(0, 10)) 
        self.entry_search.bind("<Return>", lambda e: self.handle_search())
        
        ctk.CTkButton(container, text="搜尋", width=70, height=Layout.BTN_HEIGHT, command=self.handle_search).pack(side="left")

        ctk.CTkLabel(container, text="類別篩選：", font=Font.BODY, text_color=Color.TEXT_DARK).pack(side="left", padx=(30, 10))
        self.combo_filter = ctk.CTkComboBox(container, state="readonly", width=160, height=Layout.BTN_HEIGHT, command=self.handle_filter_change)
        self.combo_filter.set("顯示全部")
        self.combo_filter.pack(side="left")
        
        ctk.CTkButton(container, text="重置", fg_color=Color.GRAY_BUTTON, text_color=Color.TEXT_DARK, hover_color=Color.GRAY_BUTTON_HOVER, width=60, height=Layout.BTN_HEIGHT, command=self.reset_filters).pack(side="left", padx=10)
        ctk.CTkButton(container, text="批次貼上", fg_color=Color.INFO, width=90, height=Layout.BTN_HEIGHT, command=self.open_bulk_paste_dialog).pack(side="left", padx=(10, 0))

    def bind_submit_shortcuts(self):
        self.entry_name.bind("<Return>", lambda _e: self.entry_price.focus_set())
        self.entry_price.bind("<Return>", lambda _e: self.entry_cost.focus_set())
        self.entry_cost.bind("<Return>", lambda _e: self.entry_life.focus_set())
        self.entry_life.bind("<Return>", lambda _e: self.handle_update() if self.selected_id else self.handle_add())

    def open_bulk_paste_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("批次貼上產品")
        dialog.geometry("760x520")
        dialog.lift()

        ctk.CTkLabel(
            dialog,
            text="每行一筆：名稱,類別,售價,成本,保存期限",
            font=Font.BODY,
            text_color=Color.TEXT_DARK,
        ).pack(anchor="w", padx=16, pady=(12, 6))
        ctk.CTkLabel(
            dialog,
            text="也支援 Tab 分隔；只填名稱時其餘欄位自動帶入預設。",
            font=Font.SMALL,
            text_color=Color.TEXT_LIGHT,
        ).pack(anchor="w", padx=16, pady=(0, 8))

        textbox = ctk.CTkTextbox(dialog)
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        button_row = ctk.CTkFrame(dialog, fg_color="transparent")
        button_row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(
            button_row,
            text="下載範本",
            width=100,
            fg_color=Color.GRAY_BUTTON,
            text_color=Color.TEXT_DARK,
            hover_color=Color.GRAY_BUTTON_HOVER,
            command=self.download_bulk_template,
        ).pack(side="left")
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
        parsed_rows = []
        errors = []

        for idx, line in enumerate(lines, start=1):
            parts = [p.strip() for p in (line.split("\t") if "\t" in line else line.split(","))]
            name = clean_text(parts[0]) if len(parts) >= 1 else ""
            category = clean_text(parts[1]) if len(parts) >= 2 and clean_text(parts[1]) else default_category
            price_raw = parts[2] if len(parts) >= 3 else "0"
            cost_raw = parts[3] if len(parts) >= 4 else "0"
            life_raw = parts[4] if len(parts) >= 5 else ""

            if not name:
                errors.append(f"第 {idx} 行：產品名稱空白")
                continue

            price, err = parse_non_negative_float(price_raw, "售價")
            if err:
                errors.append(f"第 {idx} 行：{err}")
                continue
            cost, err = parse_non_negative_float(cost_raw, "成本")
            if err:
                errors.append(f"第 {idx} 行：{err}")
                continue
            life, err = parse_optional_non_negative_int(life_raw, "保存期限")
            if err:
                errors.append(f"第 {idx} 行：{err}")
                continue

            parsed_rows.append((idx, name, category, price, cost, life))

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

        default_category = clean_text(self.combo_category.get()) or "其他"
        ok_count = 0
        fail_count = len(errors)

        for idx, name, category, price, cost, life in parsed_rows:
            success, msg = add_product(name, category, price, cost, life)
            if success:
                ok_count += 1
            else:
                fail_count += 1
                errors.append(f"第 {idx} 行：{msg}")

        self.refresh_table()
        self.refresh_filter_options()
        if ok_count > 0:
            self.combo_category.set(default_category)
            self.__class__.LAST_CATEGORY = default_category
        summary = f"成功 {ok_count} 筆，失敗 {fail_count} 筆"
        if errors:
            summary += "\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                summary += f"\n...其餘 {len(errors)-10} 筆錯誤省略"
        messagebox.showinfo("批次匯入結果", summary)
        dialog.destroy()

    def download_bulk_template(self):
        file_path = filedialog.asksaveasfilename(
            title="下載產品批次匯入範本",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="products_bulk_template.csv",
        )
        if not file_path:
            return
        lines = [
            "名稱,類別,售價,成本,保存期限",
            "檸檬塔,常溫蛋糕/塔,160,75,3",
            "草莓鮮奶油蛋糕,整模蛋糕,980,420,2",
            "奶油餅乾,常溫餅乾,55,20,30",
        ]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        messagebox.showinfo("完成", f"範本已儲存：\n{file_path}")

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
        self.tree.bind("<Double-1>", self.on_tree_double_click)

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
    def on_tree_double_click(self, _event):
        self.on_tree_select(None)
        self.entry_name.focus_set()
    def deselect_item(self):
        self.selected_id = None; self.clear_form()
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        self.edit_btn_group.pack_forget(); self.btn_add.pack(side="right")
    def handle_add(self):
        name = clean_text(self.entry_name.get()); cat = clean_text(self.combo_category.get()); p_str = self.entry_price.get(); c_str = self.entry_cost.get(); l_str = self.entry_life.get()
        if not name or not p_str: messagebox.showwarning("欄位未填", "請填寫名稱與售價"); return
        p, err = parse_non_negative_float(p_str, "售價")
        if err: messagebox.showerror("格式錯誤", err); return
        c, err = parse_non_negative_float(c_str, "成本")
        if err: messagebox.showerror("格式錯誤", err); return
        l, err = parse_optional_non_negative_int(l_str, "保存期限")
        if err: messagebox.showerror("格式錯誤", err); return
        success, msg = add_product(name, cat, p, c, l)
        if success: self.__class__.LAST_CATEGORY = cat or self.__class__.LAST_CATEGORY; self.clear_form(); self.refresh_table(); self.refresh_filter_options(); self.combo_category.set(self.__class__.LAST_CATEGORY); self.entry_name.focus_set()
        else: messagebox.showerror("錯誤", msg)
    def handle_update(self):
        if not self.selected_id: return
        name = clean_text(self.entry_name.get()); cat = clean_text(self.combo_category.get()); p_str = self.entry_price.get(); c_str = self.entry_cost.get(); l_str = self.entry_life.get()
        if not name or not p_str: messagebox.showwarning("欄位未填", "請填寫名稱與售價"); return
        p, err = parse_non_negative_float(p_str, "售價")
        if err: messagebox.showerror("格式錯誤", err); return
        c, err = parse_non_negative_float(c_str, "成本")
        if err: messagebox.showerror("格式錯誤", err); return
        l, err = parse_optional_non_negative_int(l_str, "保存期限")
        if err: messagebox.showerror("格式錯誤", err); return
        success, msg = update_product(self.selected_id, name, cat, p, c, l)
        if success: self.__class__.LAST_CATEGORY = cat or self.__class__.LAST_CATEGORY; messagebox.showinfo("成功", "已更新"); self.deselect_item(); self.refresh_table(); self.refresh_filter_options(); self.combo_category.set(self.__class__.LAST_CATEGORY); self.entry_name.focus_set()
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
