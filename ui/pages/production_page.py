import customtkinter as ctk
from tkinter import messagebox

from logic.items_logic import list_finished_items
from logic.production_logic import produce_product


class ProductionPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        title = ctk.CTkLabel(self, text="生產管理", font=("Arial", 22))
        title.pack(pady=10)

        # ==============================
        # 選擇成品
        # ==============================
        product_frame = ctk.CTkFrame(self)
        product_frame.pack(pady=10)

        ctk.CTkLabel(product_frame, text="選擇成品：", width=100).grid(row=0, column=0, padx=5)

        self.product_var = ctk.StringVar()

        product_list = self.get_product_list()
        self.product_menu = ctk.CTkOptionMenu(
            product_frame,
            values=product_list,
            variable=self.product_var,
            width=250
        )
        self.product_menu.grid(row=0, column=1, padx=5)

        # ==============================
        # 生產數量
        # ==============================
        qty_frame = ctk.CTkFrame(self)
        qty_frame.pack(pady=10)

        ctk.CTkLabel(qty_frame, text="生產數量：", width=100).grid(row=0, column=0, padx=5)

        self.qty_entry = ctk.CTkEntry(qty_frame, width=100)
        self.qty_entry.grid(row=0, column=1, padx=5)

        # ==============================
        # 生產按鈕
        # ==============================
        produce_btn = ctk.CTkButton(
            self,
            text="開始生產",
            font=("Arial", 16),
            command=self.start_production
        )
        produce_btn.pack(pady=20)

        # ==============================
        # 生產結果（LOT顯示）
        # ==============================
        self.result_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.result_label.pack(pady=10)

    # =======================================================
    # 取得成品列表（供選擇）
    # =======================================================
    def get_product_list(self):
        products = list_finished_items()
        return [f"{p['item_id']}｜{p['name']}" for p in products]

    # =======================================================
    # 生產流程
    # =======================================================
    def start_production(self):
        data = self.product_var.get()
        if not data:
            messagebox.showerror("錯誤", "請先選擇成品")
            return

        product_id = data.split("｜")[0].strip()

        qty_text = self.qty_entry.get()

        try:
            qty = float(qty_text)
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showerror("錯誤", "請輸入正確的生產數量")
            return

        # 呼叫後端生產邏輯
        lot = produce_product(product_id, qty)

        # 顯示結果
        self.result_label.configure(
            text=f"生產成功！\nLOT 號：{lot}\n品項：{product_id}\n數量：{qty}"
        )

        self.qty_entry.delete(0, "end")
