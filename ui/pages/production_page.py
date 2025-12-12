import customtkinter as ctk
from tkinter import messagebox

from logic.products_logic import get_all_products
from logic.production_logic import check_production_capacity, produce


class ProductionPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="產品生產",
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        form = ctk.CTkFrame(self)
        form.pack(pady=10)

        # 產品選單
        ctk.CTkLabel(form, text="產品：").grid(row=0, column=0, padx=5)
        self.products = get_all_products()
        names = [p["name"] for p in self.products]

        self.prod_box = ctk.CTkComboBox(form, values=names, width=220)
        self.prod_box.grid(row=0, column=1, padx=5)

        # 批數
        ctk.CTkLabel(form, text="批數：").grid(row=1, column=0, padx=5)
        self.batch_entry = ctk.CTkEntry(form, width=120)
        self.batch_entry.grid(row=1, column=1, padx=5)

        ctk.CTkButton(form, text="執行生產",
                      command=self.do_production).grid(row=2, column=0, columnspan=2, pady=10)

    # --------------------------------------------------
    # 執行生產
    # --------------------------------------------------
    def do_production(self):
        name = self.prod_box.get()
        prod = next((p for p in self.products if p["name"] == name), None)
        batch = int(self.batch_entry.get())

        lack = check_production_capacity(prod["id"], batch)
        if lack:
            msg = "庫存不足，無法生產：\n"
            for item in lack:
                msg += f"{item['name']}：需要 {item['required']}，現有 {item['current']}\n"
            messagebox.showerror("錯誤", msg)
            return

        ok, msg = produce(prod["id"], batch)
        messagebox.showinfo("生產完成", msg)
