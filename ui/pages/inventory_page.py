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

        # ======== 表單區域 ========
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(padx=20, pady=10, fill="x")

        # 原料下拉式選單
        ctk.CTkLabel(form_frame, text="原料：").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.material_values = get_material_dropdown_list()

        self.material_dropdown = ctk.CTkComboBox(
            form_frame,
            values=[label for _, label in self.material_values],
            width=250
        )
        self.material_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # 數量
        ctk.CTkLabel(form_frame, text="數量：").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_qty = ctk.CTkEntry(form_frame, width=150)
        self.entry_qty.grid(row=1, column=1, padx=5, pady=5)

        # 單價
        ctk.CTkLabel(form_frame, text="單價：").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_cost = ctk.CTkEntry(form_frame, width=150)
        self.entry_cost.grid(row=1, column=3, padx=5, pady=5)

        # 供應商
        ctk.CTkLabel(form_frame, text="供應商：").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_supplier = ctk.CTkEntry(form_frame, width=250)
        self.entry_supplier.grid(row=2, column=1, padx=5, pady=5)

        # 備註
        ctk.CTkLabel(form_frame, text="備註：").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.entry_note = ctk.CTkEntry(form_frame, width=250)
        self.entry_note.grid(row=2, column=3, padx=5, pady=5)

        # ======== 按鈕 ========
        btn = ctk.CTkButton(form_frame, text="新增入庫", command=self.save_inbound)
        btn.grid(row=3, column=0, columnspan=4, pady=15)

        # ======== 紀錄表格 ========
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        columns = ("id", "name", "qty", "unit_cost", "subtotal", "supplier", "note", "time")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.table.heading("id", text="ID")
        self.table.heading("name", text="原料")
        self.table.heading("qty", text="數量")
        self.table.heading("unit_cost", text="單價")
        self.table.heading("subtotal", text="小計")
        self.table.heading("supplier", text="供應商")
        self.table.heading("note", text="備註")
        self.table.heading("time", text="時間")

        self.table.pack(expand=True, fill="both")

        self.load_inbound_table()

    # ---------------------------------------------------------
    # 新增入庫紀錄
    # ---------------------------------------------------------
    def save_inbound(self):
        # 抓 material_id
        selected_label = self.material_dropdown.get()
        mat_dict = dict(self.material_values)  # {id: label}
        material_id = None

        for mid, label in self.material_values:
            if label == selected_label:
                material_id = mid
                break

        if material_id is None:
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
            self.load_inbound_table()

    # ---------------------------------------------------------
    # 重置表單
    # ---------------------------------------------------------
    def reset_form(self):
        self.entry_qty.delete(0, "end")
        self.entry_cost.delete(0, "end")
        self.entry_supplier.delete(0, "end")
        self.entry_note.delete(0, "end")

    # ---------------------------------------------------------
    # 載入入庫紀錄表格
    # ---------------------------------------------------------
    def load_inbound_table(self):
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
