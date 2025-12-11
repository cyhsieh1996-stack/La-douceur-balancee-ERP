import customtkinter as ctk
from logic.inventory_logic import get_all_inventory


class InventoryPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Title
        title = ctk.CTkLabel(self, text="庫存總覽", font=("Arial", 20))
        title.pack(pady=10)

        # 搜尋列
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(search_frame, text="搜尋品項：").pack(side="left", padx=5)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_inventory())

        # 表格區域
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 表頭
        header = ctk.CTkFrame(self.table_frame)
        header.pack(fill="x")

        headers = ["代碼", "名稱", "分類", "庫存", "單位", "安全庫存"]
        widths = [80, 200, 120, 80, 70, 100]

        for i, (h, w) in enumerate(zip(headers, widths)):
            lbl = ctk.CTkLabel(header, text=h, width=w)
            lbl.grid(row=0, column=i, padx=3)

        # 內容表格
        self.body = ctk.CTkFrame(self.table_frame)
        self.body.pack(fill="both", expand=True, pady=5)

        self.load_inventory()

    # ============================================================
    # 載入庫存
    # ============================================================
    def load_inventory(self):
        for w in self.body.winfo_children():
            w.destroy()

        keyword = self.search_var.get().strip()

        inventory = get_all_inventory()

        # 過濾搜尋
        if keyword:
            inventory = [i for i in inventory if keyword in i["name"] or keyword in i["item_id"]]

        # 顯示每一列
        for row in inventory:
            frame = ctk.CTkFrame(self.body)
            frame.pack(fill="x", pady=2)

            # 庫存顯示濾色
            stock_color = "red" if row["low_stock"] else "white"

            fields = [
                row["item_id"],
                row["name"],
                row["category"],
                row["stock"],
                row["unit"],
                row["safety_stock"] if row["safety_stock"] else "-"
            ]

            widths = [80, 200, 120, 80, 70, 100]

            for i, (text, w) in enumerate(zip(fields, widths)):
                lbl = ctk.CTkLabel(frame, text=str(text), width=w)
                if i == 3:  # 庫存欄位
                    lbl.configure(text_color=stock_color)
                lbl.grid(row=0, column=i, padx=3)
