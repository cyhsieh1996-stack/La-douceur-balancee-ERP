import customtkinter as ctk
from tkinter import ttk, messagebox

from logic.products_logic import (
    get_all_products,
    add_product,
    update_product,
    delete_product,
)


class ProductsPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(
            self, text="產品管理",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=20)

        # ----------------------------------------
        # 新增產品表單
        # ----------------------------------------
        form = ctk.CTkFrame(self)
        form.pack(fill="x", pady=10, padx=20)

        labels = ["產品名稱", "類別", "售價"]
        self.entries = []

        for i, lb in enumerate(labels):
            ctk.CTkLabel(form, text=lb).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ctk.CTkEntry(form, width=250)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(entry)

        add_btn = ctk.CTkButton(form, text="新增產品", command=self.add_product)
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # ----------------------------------------
        # 產品列表表格
        # ----------------------------------------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "name", "category", "price")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = ["ID", "產品名稱", "類別", "售價"]
        for col, h in zip(columns, headers):
            self.table.heading(col, text=h)

        self.table.pack(fill="both", expand=True)

        # 雙擊啟動編輯
        self.table.bind("<Double-1>", self.on_edit)

        self.load_products()

    # ----------------------------------------
    # 載入產品列表
    # ----------------------------------------
    def load_products(self):
        for row in self.table.get_children():
            self.table.delete(row)

        products = get_all_products()

        for p in products:
            self.table.insert("", "end", values=(
                p["id"], p["name"], p["category"], p["price"]
            ))

    # ----------------------------------------
    # 新增產品
    # ----------------------------------------
    def add_product(self):
        vals = [e.get() for e in self.entries]

        if not vals[0]:
            messagebox.showerror("錯誤", "產品名稱不可空白")
            return

        ok, msg = add_product(vals[0], vals[1], vals[2])
        messagebox.showinfo("訊息", msg)

        self.load_products()

    # ----------------------------------------
    # 編輯產品
    # ----------------------------------------
    def on_edit(self, event):
        selected = self.table.focus()
        if not selected:
            return

        vals = self.table.item(selected, "values")
        prod_id = vals[0]

        win = ctk.CTkToplevel(self)
        win.title("編輯產品")
        win.geometry("400x350")

        fields = ["產品名稱", "類別", "售價"]
        entries = []

        for i, lb in enumerate(fields):
            ctk.CTkLabel(win, text=lb).pack(pady=5)
            ent = ctk.CTkEntry(win)
            ent.insert(0, vals[i+1])
            ent.pack(pady=5)
            entries.append(ent)

        def save_edit():
            data = [e.get() for e in entries]
            ok, msg = update_product(prod_id, data[0], data[1], data[2])
            messagebox.showinfo("訊息", msg)
            win.destroy()
            self.load_products()

        def delete_prod():
            ok, msg = delete_product(prod_id)
            messagebox.showinfo("訊息", msg)
            win.destroy()
            self.load_products()

        ctk.CTkButton(win, text="儲存變更", command=save_edit).pack(pady=10)
        ctk.CTkButton(win, text="刪除此產品", fg_color="red",
                      command=delete_prod).pack(pady=5)
