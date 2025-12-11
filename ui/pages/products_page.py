import customtkinter as ctk
from logic.products_logic import (
    get_all_products,
    add_product,
    update_product,
    delete_product,
)

class ProductsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        title = ctk.CTkLabel(self, text="商品管理", font=("Microsoft JhengHei", 24))
        title.pack(pady=10)

        # 商品列表
        self.product_listbox = ctk.CTkTextbox(self, height=400, width=600)
        self.product_listbox.pack(pady=10)

        # 載入資料
        self.load_products()

        # 操作按鈕
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="新增商品", command=self.open_add_window).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="修改選取商品", command=self.open_edit_window).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="刪除選取商品", command=self.delete_selected).grid(row=0, column=2, padx=10)

    # ========================
    # 讀取商品資料
    # ========================
    def load_products(self):
        self.product_listbox.delete("1.0", "end")

        products = get_all_products()
        for p in products:
            self.product_listbox.insert(
                "end",
                f"{p['item_id']} | {p['name']} | {p['category']} | {p['unit']} | 成本:{p['cost']}\n"
            )

    # ========================
    # 新增商品窗口
    # ========================
    def open_add_window(self):
        win = ctk.CTkToplevel(self)
        win.title("新增商品")

        fields = {
            "item_id": ctk.CTkEntry(win),
            "name": ctk.CTkEntry(win),
            "category": ctk.CTkEntry(win),
            "unit": ctk.CTkEntry(win),
            "cost": ctk.CTkEntry(win),
            "safety_stock": ctk.CTkEntry(win)
        }

        row = 0
        for label, widget in fields.items():
            ctk.CTkLabel(win, text=label).grid(row=row, column=0, padx=5, pady=5)
            widget.grid(row=row, column=1, padx=5, pady=5)
            row += 1

        def submit():
            add_product(
                fields["item_id"].get(),
                fields["name"].get(),
                fields["category"].get(),
                fields["unit"].get(),
                float(fields["cost"].get() or 0),
                float(fields["safety_stock"].get() or 0),
            )
            win.destroy()
            self.load_products()

        ctk.CTkButton(win, text="確認新增", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    # ========================
    # 修改商品
    # ========================
    def open_edit_window(self):
        pass  # 之後依需求補完

    # ========================
    # 刪除商品
    # ========================
    def delete_selected(self):
        pass  # 之後依需求補完
