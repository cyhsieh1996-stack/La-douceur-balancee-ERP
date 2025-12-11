import tkinter as tk
from tkinter import ttk, messagebox
from logic.inbound_logic import record_inbound, list_inbound_records
from logic.items_logic import list_raw_materials   # ★★★ 唯一需要的列表

class InboundPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        # Title
        tk.Label(self, text="原料進貨（Inbound）", font=("Arial", 16, "bold"), bg="white").pack(pady=15)

        # Form frame
        form = tk.Frame(self, bg="white")
        form.pack(pady=10)

        # ========================
        # 原料選擇下拉選單
        # ========================
        tk.Label(form, text="原料項目：", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.item_var = tk.StringVar()

        items = list_raw_materials()     # ★★★ 這裡改成 raw materials ★★★
        self.item_map = {f"{i['name']} ({i['item_id']})": i["item_id"] for i in items}

        self.item_combo = ttk.Combobox(form, textvariable=self.item_var, values=list(self.item_map.keys()), width=40)
        self.item_combo.grid(row=0, column=1, padx=5, pady=5)

        # ========================
        # 數量
        # ========================
        tk.Label(form, text="進貨數量：", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.qty_entry = tk.Entry(form)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)

        # ========================
        # 批號
        # ========================
        tk.Label(form, text="批號（Lot No.）：", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.lot_entry = tk.Entry(form)
        self.lot_entry.grid(row=2, column=1, padx=5, pady=5)

        # ========================
        # 按鈕
        # ========================
        tk.Button(form, text="新增進貨紀錄", command=self.save_inbound, bg="#3E8E41", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

        # ========================
        # 下方：歷史紀錄列表
        # ========================
        self.table = ttk.Treeview(self, columns=("date", "item", "qty", "lot"), show="headings", height=10)
        self.table.pack(fill=tk.BOTH, expand=True, pady=15)

        self.table.heading("date", text="日期")
        self.table.heading("item", text="原料")
        self.table.heading("qty", text="數量")
        self.table.heading("lot", text="Lot No.")

        self.refresh_table()

    # ------------------------------------------------------------

    def save_inbound(self):
        item_text = self.item_var.get()
        if item_text not in self.item_map:
            messagebox.showerror("錯誤", "請選擇原料項目")
            return

        item_id = self.item_map[item_text]

        try:
            qty = float(self.qty_entry.get())
        except:
            messagebox.showerror("錯誤", "數量必須是數字")
            return

        lot = self.lot_entry.get().strip()

        record_inbound(item_id, qty, lot)

        messagebox.showinfo("成功", "已新增進貨紀錄")
        self.refresh_table()

    # ------------------------------------------------------------

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        rows = list_inbound_records()

        for r in rows:
            self.table.insert("", "end", values=(r["date"], r["item_name"], r["qty_in"], r["lot_number"]))
