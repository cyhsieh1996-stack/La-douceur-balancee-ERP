import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font
from logic.raw_materials_logic import get_all_materials
from logic.inventory_logic import (
    adjust_stock,
    get_inventory_snapshot,
    get_inventory_summary,
    get_material_stock,
    get_recent_adjustments,
)
from ui.input_utils import clean_text, parse_non_negative_float

class InventoryPage(ctk.CTkFrame):
    LAST_MATERIAL = ""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_mat_id = None

        self.create_header()
        self.create_summary_cards()
        self.create_stock_center()
        self.create_adjustment_form()
        self.create_history_section()

        self.load_materials()
        self.refresh_summary()
        self.refresh_stock_table()
        self.refresh_history_table()
        self.bind_submit_shortcuts()
        self.actual_stock_entry.focus_set()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=18, border_width=1, border_color=Color.BORDER)
        header.pack(fill="x", pady=(0, 16))
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=18)
        ctk.CTkLabel(title_box, text="庫存中心", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(
            title_box,
            text="集中查看原料現況、低庫存警示與盤點異動，並可直接從表格進行修正。",
            font=Font.BODY,
            text_color=Color.TEXT_LIGHT,
        ).pack(anchor="w", pady=(4, 0))

        action_box = ctk.CTkFrame(header, fg_color="transparent")
        action_box.pack(side="right", padx=20, pady=18)
        ctk.CTkButton(
            action_box,
            text="重整資料",
            fg_color=Color.GRAY_BUTTON,
            hover_color=Color.GRAY_BUTTON_HOVER,
            text_color=Color.TEXT_DARK,
            width=100,
            height=36,
            command=self.refresh_all,
        ).pack(side="left")

    def create_summary_cards(self):
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", pady=(0, 16))
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.summary_labels = {}
        self.create_summary_card("原料總數", "material_count", "目前原料主檔筆數", 0)
        self.create_summary_card("低庫存警示", "low_stock_count", "低於安全庫存", 1)
        self.create_summary_card("零庫存", "zero_stock_count", "需要確認是否停用或補貨", 2)
        self.create_summary_card("估算庫存值", "estimated_stock_value", "依最新進貨單價估算", 3)

    def create_summary_card(self, title, key, hint, col):
        card = ctk.CTkFrame(self.summary_frame, fg_color=Color.WHITE_CARD, corner_radius=16, border_width=1, border_color=Color.BORDER)
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(anchor="w", padx=16, pady=(14, 4))
        value_label = ctk.CTkLabel(card, text="0", font=Font.STAT_NUMBER, text_color=Color.PRIMARY)
        value_label.pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=hint, font=Font.SMALL, text_color=Color.TEXT_LIGHT).pack(anchor="w", padx=16, pady=(4, 14))
        self.summary_labels[key] = value_label

    def create_stock_center(self):
        self.stock_frame = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=14, border_width=1, border_color=Color.BORDER)
        self.stock_frame.pack(fill="both", expand=True, pady=(0, 16))

        top = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 10))
        title_box = ctk.CTkFrame(top, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="即時庫存清單", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(title_box, text="雙擊表格可直接帶入下方盤點修正區。", font=Font.SMALL, text_color=Color.TEXT_LIGHT).pack(anchor="w", pady=(2, 0))

        filter_box = ctk.CTkFrame(top, fg_color="transparent")
        filter_box.pack(side="right")
        self.search_entry = ctk.CTkEntry(filter_box, width=220, placeholder_text="搜尋名稱、類別、廠商、廠牌")
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda _e: self.refresh_stock_table())
        self.low_stock_only_var = ctk.StringVar(value="off")
        self.low_stock_switch = ctk.CTkSwitch(
            filter_box,
            text="只看低庫存",
            variable=self.low_stock_only_var,
            onvalue="on",
            offvalue="off",
            command=self.refresh_stock_table,
        )
        self.low_stock_switch.pack(side="left", padx=(0, 8))
        ctk.CTkButton(filter_box, text="搜尋", width=70, height=32, command=self.refresh_stock_table).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            filter_box,
            text="清除",
            width=70,
            height=32,
            fg_color=Color.GRAY_BUTTON,
            hover_color=Color.GRAY_BUTTON_HOVER,
            text_color=Color.TEXT_DARK,
            command=self.clear_stock_filters,
        ).pack(side="left")

        table_wrap = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
        table_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        columns = ("name", "category", "vendor", "stock", "safe", "diff", "unit", "price")
        headers = ["原料名稱", "類別", "廠商", "目前庫存", "安全庫存", "距安全量", "單位", "參考單價"]
        widths = [180, 90, 120, 90, 90, 90, 60, 90]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")

        self.stock_tree = ttk.Treeview(table_wrap, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.stock_tree.heading(col, text=h)
            self.stock_tree.column(col, width=w, anchor="center")
        self.stock_tree.tag_configure("odd", background="white")
        self.stock_tree.tag_configure("even", background=Color.TABLE_ROW_ALT)
        self.stock_tree.tag_configure("warning", background="#FEF3C7")
        self.stock_tree.bind("<<TreeviewSelect>>", self.on_stock_tree_select)
        self.stock_tree.bind("<Double-1>", self.on_stock_tree_activate)

        scroll_y = ttk.Scrollbar(table_wrap, orient="vertical", command=self.stock_tree.yview)
        scroll_x = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.stock_tree.xview)
        self.stock_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.stock_tree.pack(side="left", fill="both", expand=True)

    def create_adjustment_form(self):
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=14, border_width=1, border_color=Color.BORDER)
        self.form_card.pack(fill="x", pady=(0, 16))
        container = ctk.CTkFrame(self.form_card, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=20)
        lbl_style = {"font": Font.BODY, "text_color": Color.TEXT_DARK, "anchor": "w"}

        ctk.CTkLabel(container, text="選擇原料", **lbl_style).grid(row=0, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(container, text="系統目前庫存", **lbl_style).grid(row=0, column=1, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(container, text="實際盤點數量", **lbl_style).grid(row=0, column=2, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(container, text="調整原因 / 備註", **lbl_style).grid(row=0, column=3, padx=10, pady=(0, 5), sticky="w")

        self.material_cb = ctk.CTkComboBox(container, values=[], width=220, command=self.on_material_select, state="readonly")
        self.material_cb.grid(row=1, column=0, padx=10, pady=(0, 12), sticky="w")

        self.current_stock_lbl = ctk.CTkLabel(container, text="---", font=Font.BODY_BOLD, text_color=Color.PRIMARY)
        self.current_stock_lbl.grid(row=1, column=1, padx=10, pady=(0, 12), sticky="w")

        self.actual_stock_entry = ctk.CTkEntry(container, width=180, placeholder_text="輸入修正後數量")
        self.actual_stock_entry.grid(row=1, column=2, padx=10, pady=(0, 12), sticky="w")

        self.reason_entry = ctk.CTkEntry(container, width=260, placeholder_text="例如：盤點差異、破損、過期報廢")
        self.reason_entry.grid(row=1, column=3, padx=10, pady=(0, 12), sticky="w")

        self.adjustment_hint = ctk.CTkLabel(container, text="可從上方即時庫存清單選取原料，自動帶入目前庫存。", font=Font.SMALL, text_color=Color.TEXT_LIGHT)
        self.adjustment_hint.grid(row=2, column=0, columnspan=3, padx=10, sticky="w")

        self.btn_submit = ctk.CTkButton(container, text="確認調整", fg_color=Color.DANGER, width=120, height=38, command=self.submit)
        self.btn_submit.grid(row=1, column=4, padx=10, pady=(0, 12), sticky="e")

    def create_history_section(self):
        ctk.CTkLabel(self, text="最近盤點異動", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 8))
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=14, border_width=1, border_color=Color.BORDER)
        self.table_card.pack(fill="both", expand=True)
        container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("date", "name", "old", "new", "diff", "unit", "reason")
        headers = ["日期", "原料名稱", "原本庫存", "盤點後庫存", "增減量", "單位", "原因"]
        widths = [140, 150, 80, 80, 80, 50, 200]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=35, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")

        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")

        self.tree.tag_configure("odd", background="white")
        self.tree.tag_configure("even", background=Color.TABLE_ROW_ALT)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def bind_submit_shortcuts(self):
        self.search_entry.bind("<Return>", lambda _e: self.refresh_stock_table())
        self.actual_stock_entry.bind("<Return>", lambda _e: self.reason_entry.focus_set())
        self.reason_entry.bind("<Return>", lambda _e: self.submit())

    def load_materials(self):
        self.materials = get_all_materials()
        items = [m['name'] for m in self.materials]
        self.material_cb.configure(values=items)
        if items: 
            default_material = self.LAST_MATERIAL if self.LAST_MATERIAL in items else items[0]
            self.material_cb.set(default_material)
            self.on_material_select(default_material)

    def on_material_select(self, choice):
        mat = next((m for m in self.materials if m['name'] == choice), None)
        if mat:
            stock, unit = get_material_stock(mat['id'])
            stock_fmt = int(stock) if float(stock).is_integer() else round(stock, 3)
            self.current_stock_lbl.configure(text=f"{stock_fmt} {unit}")
            self.selected_mat_id = mat['id']
            self.__class__.LAST_MATERIAL = mat['name']
            self.adjustment_hint.configure(text=f"目前選擇：{mat['name']}，可直接輸入盤點後的實際數量。")

    def on_stock_tree_select(self, _event):
        selected = self.stock_tree.selection()
        if not selected:
            return
        item_id = selected[0]
        material_name = self.stock_tree.item(item_id, "values")[0]
        self.material_cb.set(material_name)
        self.on_material_select(material_name)

    def on_stock_tree_activate(self, _event):
        self.on_stock_tree_select(None)
        selected = self.stock_tree.selection()
        if not selected:
            return
        values = self.stock_tree.item(selected[0], "values")
        self.actual_stock_entry.delete(0, "end")
        self.actual_stock_entry.insert(0, values[3])
        self.actual_stock_entry.focus_set()

    def refresh_summary(self):
        summary = get_inventory_summary()
        self.summary_labels["material_count"].configure(text=str(summary["material_count"]))
        self.summary_labels["low_stock_count"].configure(text=str(summary["low_stock_count"]))
        self.summary_labels["zero_stock_count"].configure(text=str(summary["zero_stock_count"]))
        self.summary_labels["estimated_stock_value"].configure(text=f"${self.format_number(summary['estimated_stock_value'])}")

    def refresh_stock_table(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        rows = get_inventory_snapshot(
            keyword=clean_text(self.search_entry.get()),
            low_stock_only=self.low_stock_only_var.get() == "on",
        )
        for i, row in enumerate(rows):
            stock = self.format_number(row["stock"])
            safe = self.format_number(row["safe_stock"])
            diff = self.format_signed_number(row["balance_to_safe"])
            price = self.format_number(row["unit_price"])
            values = (
                row["name"],
                row["category"] or "",
                row["vendor"] or "",
                stock,
                safe,
                diff,
                row["unit"] or "",
                price,
            )
            if row["safe_stock"] > 0 and row["stock"] < row["safe_stock"]:
                tag = "warning"
            else:
                tag = "even" if i % 2 == 0 else "odd"
            self.stock_tree.insert("", "end", iid=str(row["id"]), values=values, tags=(tag,))

    def refresh_history_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_recent_adjustments(20)
        for i, row in enumerate(rows):
            vals = (
                row[0][:16],
                row[1],
                self.format_number(row[2]),
                self.format_number(row[3]),
                self.format_signed_number(row[4]),
                row[5],
                row[6],
            )
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def refresh_all(self):
        self.load_materials()
        self.refresh_summary()
        self.refresh_stock_table()
        self.refresh_history_table()

    def clear_stock_filters(self):
        self.search_entry.delete(0, "end")
        self.low_stock_only_var.set("off")
        self.refresh_stock_table()

    def format_number(self, value):
        try:
            num = float(value)
            return str(int(num)) if num.is_integer() else f"{num:.3f}".rstrip("0").rstrip(".")
        except Exception:
            return str(value)

    def format_signed_number(self, value):
        try:
            num = float(value)
            formatted = self.format_number(num)
            return f"+{formatted}" if num > 0 else formatted
        except Exception:
            return str(value)

    def submit(self):
        if not self.selected_mat_id:
            messagebox.showwarning("警告", "請先選擇原料")
            return
        new_stock, err = parse_non_negative_float(self.actual_stock_entry.get(), "盤點數量")
        if err:
            messagebox.showwarning("錯誤", err)
            return
        reason = clean_text(self.reason_entry.get())
        if not reason:
            messagebox.showwarning("警告", "請填寫調整原因")
            return
        success, msg = adjust_stock(self.selected_mat_id, new_stock, reason)
        if success:
            messagebox.showinfo("成功", msg)
            self.actual_stock_entry.delete(0, "end")
            self.reason_entry.delete(0, "end")
            self.on_material_select(self.material_cb.get())
            self.refresh_summary()
            self.refresh_stock_table()
            self.refresh_history_table()
            self.actual_stock_entry.focus_set()
        else:
            messagebox.showerror("失敗", msg)
