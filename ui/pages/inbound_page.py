# ui/pages/inbound_page.py

import customtkinter as ctk
from tkinter import ttk, messagebox

from logic.raw_materials_logic import get_material_dropdown_list
from logic.inbound_logic import add_inbound_record, get_all_inbound_records


class InboundPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="原料入庫", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        # ======== 表單區 ========
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(padx=20, pady=10, fill="x")

        # 原料下拉選單
        ctk.CTkLabel(form_frame, text="原料：").grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.material_values = get_material_dropdown_list()  # [(id, label), ...]
        self.material_dropdown = ctk.CTkComboBox(
            form_frame,
            values=[label for _, label in self.material_values],
            width=250
        )
        self.material_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # 數量
        ctk.CTkLabel(form_frame, text="數量：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_qty = ctk.CTkEntry(form_frame)
        self.entry_qty.grid(row=1, column=1, padx=5, pady=5)

        # 單價
        ctk.CTkLabel(form_frame, text="單價：").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_cost = ctk.CTkEntry(form_frame)
        self.entry_cost.grid(row=1, column=3, padx=5, pady=5)

        # 供應商
        ctk.CTkLabel(form_frame, text="供應商：").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_supplier = ctk.CTkEntry(form_frame)
        self.entry_supplier.grid(row=2, column=1, padx=5, pady=5)

        # 備註
        ctk.CTkLabel(form_frame, text="備註：").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.entry_note = ctk.CTkEntry(form_frame)
        self.entry_note.grid(row=2, column=3, padx=5, pady=5)

        # 儲存按鈕
        save_btn = ctk.CTkButton(form_frame, text="新增入庫", command=self.save_inbound)
        save_btn.grid(row=3, column=0, columnspan=4, pady=10)

        # ======== 紀錄表格 ========
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("id", "name", "qty", "unit_cost", "subtotal", "supplier", "note", "time")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col, text in zip(columns, ["ID", "原料", "數量", "單價", "小計", "供應商", "備註", "時間"]):
            self.table.heading(col, text=text)

        self.table.pack(fill="both", expand=True)

        self.load_inbound_records()

    # -------------------------------------------------------
    # 新增入庫紀錄
    # -------------------------------------------------------
    def save_inbound(self):
        selected_label = self.material_dropdown.get()

        # 找到 material_id
        material_id = None
        for mid, label in self.material_values:
            if label == selected_label:
                material_id = mid
                break

        if not material_id:
            messagebox.showerror("錯誤", "請選擇原料")
            return

        qty = self.entry_qty.get()
        cost = self.entry_cost.get()
        supplier = self.entry_supplier.get()
        note = self.entry_note.get()

        ok, msg = add_inbound_record(material_id, qty, cost, supplier, note)
        messagebox.showinfo("訊息", msg)

        if ok:
            self.reset_form()
            self.load_inbound_records()

    def reset_form(self):
        self.entry_qty.delete(0, "end")
        self.entry_cost.delete(0, "end")
        self.entry_supplier.delete(0, "end")
        self.entry_note.delete(0, "end")

    # -------------------------------------------------------
    # 載入表格資料
    # -------------------------------------------------------
    def load_inbound_records(self):
        for row in self.table.get_children():
            self.table.delete(row)

        records = get_all_inbound_records()

        for r in records:
            self.table.insert(
                "",
                "end",
                values=(
                    r["id"],
                    f"{r['name']}（{r['brand'] or ''}{r['spec'] or ''}）",
                    r["qty"],
                    r["unit_cost"],
                    r["subtotal"],
                    r["supplier"],
                    r["note"],
                    r["created_at"],
                )
            )
