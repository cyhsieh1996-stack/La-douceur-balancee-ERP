import customtkinter as ctk
from tkinter import ttk, messagebox

from logic.products_logic import get_all_products
from logic.raw_materials_logic import get_all_materials
from logic.recipes_logic import (
    get_recipe,
    add_recipe_item,
    delete_recipe_item,
)


class RecipesPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="食譜設定",
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        # 產品選單
        prod_frame = ctk.CTkFrame(self)
        prod_frame.pack(pady=10)

        ctk.CTkLabel(prod_frame, text="選擇產品：").grid(row=0, column=0, padx=5)

        self.products = get_all_products()
        self.product_names = [p["name"] for p in self.products]

        self.product_box = ctk.CTkComboBox(
            prod_frame, values=self.product_names, width=250)
        self.product_box.grid(row=0, column=1, padx=10)
        self.product_box.set(self.product_names[0] if self.product_names else "")

        ctk.CTkButton(prod_frame, text="載入配方",
                      command=self.load_recipe).grid(row=0, column=2, padx=10)

        # 配方表格
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "material", "amount", "unit")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = ["ID", "原料", "用量", "單位"]
        for c, h in zip(columns, headers):
            self.table.heading(c, text=h)

        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self.delete_selected)

        # 新增配方輸入區
        form = ctk.CTkFrame(self)
        form.pack(pady=20)

        ctk.CTkLabel(form, text="原料：").grid(row=0, column=0, padx=5)
        mats = get_all_materials()
        self.mat_ids = [m["id"] for m in mats]
        self.mat_names = [m["name"] for m in mats]

        self.mat_box = ctk.CTkComboBox(form, values=self.mat_names, width=200)
        self.mat_box.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(form, text="用量：").grid(row=0, column=2, padx=5)
        self.amount_entry = ctk.CTkEntry(form, width=120)
        self.amount_entry.grid(row=0, column=3, padx=5)

        ctk.CTkButton(
            form, text="新增配方", command=self.add_recipe
        ).grid(row=0, column=4, padx=10)

    # --------------------------------------------------
    # 載入配方
    # --------------------------------------------------
    def load_recipe(self):
        for r in self.table.get_children():
            self.table.delete(r)

        prod_name = self.product_box.get()
        prod_id = next((p["id"] for p in self.products if p["name"] == prod_name), None)

        rows = get_recipe(prod_id)

        for item in rows:
            self.table.insert("", "end", values=(
                item["recipe_id"],
                item["material_name"],
                item["amount"],
                item["unit"],
            ))

    # --------------------------------------------------
    # 新增配方項目
    # --------------------------------------------------
    def add_recipe(self):
        prod_name = self.product_box.get()
        prod_id = next((p["id"] for p in self.products if p["name"] == prod_name), None)

        mat_name = self.mat_box.get()
        idx = self.mat_names.index(mat_name)
        mat_id = self.mat_ids[idx]

        amount = self.amount_entry.get()

        ok, msg = add_recipe_item(prod_id, mat_id, float(amount))
        messagebox.showinfo("訊息", msg)
        self.load_recipe()

    # --------------------------------------------------
    # 刪除（雙擊列）
    # --------------------------------------------------
    def delete_selected(self, event):
        sel = self.table.focus()
        if not sel:
            return

        recipe_id = self.table.item(sel, "values")[0]
        ok, msg = delete_recipe_item(recipe_id)
        messagebox.showinfo("訊息", msg)
        self.load_recipe()
