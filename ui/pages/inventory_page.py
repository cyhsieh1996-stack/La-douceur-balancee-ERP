import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.theme import Color, Font
from logic.materials_logic import get_all_materials
from logic.inventory_logic import adjust_stock, get_recent_adjustments, get_material_stock
from ui.input_utils import clean_text, parse_non_negative_float

# 👇 這次確認這裡是 InventoryPage，不要再變成 InboundPage 了！
class InventoryPage(ctk.CTkFrame):
    LAST_MATERIAL = ""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 標題
        ctk.CTkLabel(self, text="庫存盤點與調整", font=Font.TITLE, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(0, 20))

        # 表單區
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.form_card.pack(fill="x", pady=(0, 20))
        self.create_form()

        # 歷史紀錄
        ctk.CTkLabel(self, text="最近盤點紀錄", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", pady=(10, 10))
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()

        # 載入資料
        self.load_materials()
        self.refresh_table()
        self.bind_submit_shortcuts()
        self.actual_stock_entry.focus_set()

    def create_form(self):
        container = ctk.CTkFrame(self.form_card, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=20)
        
        lbl_style = {"font": Font.BODY, "text_color": Color.TEXT_DARK, "anchor": "w"}

        # 選單與庫存
        ctk.CTkLabel(container, text="選擇原料", **lbl_style).grid(row=0, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(container, text="系統目前庫存", **lbl_style).grid(row=0, column=1, padx=10, pady=(0, 5), sticky="w")
        
        self.material_cb = ctk.CTkComboBox(container, values=[], width=250, command=self.on_material_select, state="readonly")
        self.material_cb.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="w")
        
        self.current_stock_lbl = ctk.CTkLabel(container, text="---", font=Font.BODY_BOLD, text_color=Color.PRIMARY)
        self.current_stock_lbl.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="w")

        # 輸入調整
        ctk.CTkLabel(container, text="實際盤點數量 (修正後)", **lbl_style).grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(container, text="調整原因 / 備註", **lbl_style).grid(row=2, column=1, padx=10, pady=(0, 5), sticky="w")
        
        self.actual_stock_entry = ctk.CTkEntry(container, width=250, placeholder_text="請輸入盤點後的正確數量")
        self.actual_stock_entry.grid(row=3, column=0, padx=10, pady=(0, 15), sticky="w")
        
        self.reason_entry = ctk.CTkEntry(container, width=250, placeholder_text="例如: 破損、過期報廢、盤點誤差")
        self.reason_entry.grid(row=3, column=1, padx=10, pady=(0, 15), sticky="w")

        # 按鈕
        self.btn_submit = ctk.CTkButton(container, text="確認調整", fg_color=Color.DANGER, width=120, height=38, command=self.submit)
        self.btn_submit.grid(row=3, column=2, padx=10, pady=(0, 15), sticky="e")

    def bind_submit_shortcuts(self):
        self.actual_stock_entry.bind("<Return>", lambda _e: self.reason_entry.focus_set())
        self.reason_entry.bind("<Return>", lambda _e: self.submit())

    def create_table(self):
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

        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

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
            stock_fmt = int(stock) if stock % 1 == 0 else round(stock, 3)
            self.current_stock_lbl.configure(text=f"{stock_fmt} {unit}")
            self.selected_mat_id = mat['id']
            self.__class__.LAST_MATERIAL = mat['name']

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_recent_adjustments(20)
        for i, row in enumerate(rows):
            diff = row[4]
            diff_str = f"+{diff:g}" if diff > 0 else f"{diff:g}"
            vals = (row[0][:16], row[1], f"{row[2]:g}", f"{row[3]:g}", diff_str, row[5], row[6])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def submit(self):
        if not hasattr(self, "selected_mat_id"):
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
            self.refresh_table()
            self.actual_stock_entry.focus_set()
        else:
            messagebox.showerror("失敗", msg)
