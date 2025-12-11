import customtkinter as ctk
from tkinter import messagebox

from logic.items_logic import list_finished_items, list_raw_materials
from logic.recipes_logic import (
    get_recipe,
    add_recipe_item,
    update_recipe_item,
    delete_recipe_item
)


class RecipesPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_product_id = None
        self.recipe_rows = []

        # ==============================
        # 左側區域：選擇成品
        # ==============================
        left_frame = ctk.CTkFrame(self, width=220)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="選擇成品", font=("Arial", 16)).pack(pady=5)

        self.product_listbox = ctk.CTkListbox(left_frame, width=200, height=500)
        self.product_listbox.pack(pady=5)
        self.product_listbox.bind("<<ListboxSelect>>", self.on_select_product)

        # 載入成品清單
        self.load_products()

        # ==============================
        # 右側區域：顯示 / 編輯食譜
        # ==============================
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="食譜原料清單", font=("Arial", 18)).pack(pady=5)

        # 表格標題
        header_frame = ctk.CTkFrame(right_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="原料", width=180).grid(row=0, column=0)
        ctk.CTkLabel(header_frame, text="用量", width=100).grid(row=0, column=1)
        ctk.CTkLabel(header_frame, text="單位", width=100).grid(row=0, column=2)
        ctk.CTkLabel(header_frame, text="操作", width=100).grid(row=0, column=3)

        # 表格內容
        self.recipe_table = ctk.CTkFrame(right_frame)
        self.recipe_table.pack(fill="both", expand=True, pady=10)

        # 新增原料
        add_frame = ctk.CTkFrame(right_frame)
        add_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(add_frame, text="新增原料：").grid(row=0, column=0, padx=5)

        self.new_material_var = ctk.StringVar()
        self.new_material_menu = ctk.CTkOptionMenu(
            add_frame, width=200, variable=self.new_material_var,
            values=self.get_raw_material_list()
        )
        self.new_material_menu.grid(row=0, column=1, padx=5)

        self.new_qty_entry = ctk.CTkEntry(add_frame, width=100, placeholder_text="用量")
        self.new_qty_entry.grid(row=0, column=2, padx=5)

        self.new_unit_entry = ctk.CTkEntry(add_frame, width=100, placeholder_text="單位")
        self.new_unit_entry.grid(row=0, column=3, padx=5)

        self.add_btn = ctk.CTkButton(add_frame, text="新增", command=self.add_recipe_row)
        self.add_btn.grid(row=0, column=4, padx=5)

    # ============================================================
    # 左側：載入成品
    # ============================================================
    def load_products(self):
        self.product_listbox.delete(0, "end")

        products = list_finished_items()
        for p in products:
            display = f"{p['item_id']}｜{p['name']}"
            self.product_listbox.insert("end", display)

    # ============================================================
    # 當選擇成品時載入食譜
    # ============================================================
    def on_select_product(self, event):
        if not self.product_listbox.curselection():
            return

        index = self.product_listbox.curselection()[0]
        text = self.product_listbox.get(index)

        # item_id 是｜前面的部分
        self.selected_product_id = text.split("｜")[0].strip()

        self.load_recipe_table()

    # ============================================================
    # 右側：載入食譜表格
    # ============================================================
    def load_recipe_table(self):
        for w in self.recipe_table.winfo_children():
            w.destroy()

        if not self.selected_product_id:
            return

        recipe = get_recipe(self.selected_product_id)
        self.recipe_rows = []

        for i, row in enumerate(recipe):
            self.add_recipe_row_ui(row)

    # ============================================================
    # 將一筆食譜資料（已存在 DB）呈現在表格上
    # ============================================================
    def add_recipe_row_ui(self, data):
        row_frame = ctk.CTkFrame(self.recipe_table)
        row_frame.pack(fill="x", pady=3)

        # 原料名稱
        mat_label = ctk.CTkLabel(row_frame, text=f"{data['material_id']}｜{data['material_name']}", width=180)
        mat_label.grid(row=0, column=0, padx=5)

        # 用量
        qty_entry = ctk.CTkEntry(row_frame, width=100)
        qty_entry.insert(0, str(data["qty"]))
        qty_entry.grid(row=0, column=1, padx=5)

        # 單位
        unit_entry = ctk.CTkEntry(row_frame, width=100)
        unit_entry.insert(0, data["unit"])
        unit_entry.grid(row=0, column=2, padx=5)

        # 操作（更新 / 刪除）
        update_btn = ctk.CTkButton(
            row_frame, text="更新",
            command=lambda rid=data["id"], q=qty_entry, u=unit_entry: self.update_recipe(rid, q, u)
        )
        update_btn.grid(row=0, column=3, padx=5)

        delete_btn = ctk.CTkButton(
            row_frame, text="刪除", fg_color="red",
            command=lambda rid=data["id"], f=row_frame: self.delete_recipe(rid, f)
        )
        delete_btn.grid(row=0, column=4, padx=5)

    # ============================================================
    # 新增原料 → DB
    # ============================================================
    def add_recipe_row(self):
        if not self.selected_product_id:
            messagebox.showerror("錯誤", "請先選擇一個成品")
            return

        material_id = self.new_material_var.get()
        qty = self.new_qty_entry.get()
        unit = self.new_unit_entry.get()

        if not qty or not unit:
            messagebox.showerror("錯誤", "請輸入用量與單位")
            return

        try:
            qty = float(qty)
        except:
            messagebox.showerror("錯誤", "用量必須是數字")
            return

        add_recipe_item(self.selected_product_id, material_id, qty, unit)

        self.load_recipe_table()

        self.new_qty_entry.delete(0, "end")
        self.new_unit_entry.delete(0, "end")

    # ============================================================
    # 更新原料用量
    # ============================================================
    def update_recipe(self, recipe_id, qty_entry, unit_entry):
        qty = qty_entry.get()
        unit = unit_entry.get()

        try:
            qty = float(qty)
        except:
            messagebox.showerror("錯誤", "用量必須是數字")
            return

        update_recipe_item(recipe_id, qty, unit)
        messagebox.showinfo("成功", "已更新食譜內容")

    # ============================================================
    # 刪除原料
    # ============================================================
    def delete_recipe(self, recipe_id, row_frame):
        delete_recipe_item(recipe_id)
        row_frame.destroy()

    # ============================================================
    # 取得所有原料（用於新增區）
    # ============================================================
    def get_raw_material_list(self):
        materials = list_raw_materials()
        return [m["item_id"] for m in materials]
