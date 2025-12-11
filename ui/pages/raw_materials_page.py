# ui/pages/raw_materials_page.py

import customtkinter as ctk
from tkinter import messagebox, ttk

from logic.raw_materials_logic import (
    get_all_materials,
    add_material,
    update_material,
    delete_material,
)


class RawMaterialsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # ===== 標題 =====
        title = ctk.CTkLabel(self, text="原料管理", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        # ===== 新增/編輯表單 =====
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=20, pady=10)

        # 內部欄位
        self.selected_material_id = None  # 用來紀錄目前是否在編輯

        # 原料名稱
        ctk.CTkLabel(form_frame, text="名稱：").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_name = ctk.CTkEntry(form_frame, width=200)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        # 品牌
        ctk.CTkLabel(form_frame, text="品牌：").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_brand = ctk.CTkEntry(form_frame, width=200)
        self.entry_brand.grid(row=0, column=3, padx=5, pady=5)

        # 規格
        ctk.CTkLabel(form_frame, text="規格：").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_spec = ctk.CTkEntry(form_frame, width=200)
        self.entry_spec.grid(row=1, column=1, padx=5, pady=5)

        # 單位
        ctk.CTkLabel(form_frame, text="單位：").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_unit = ctk.CTkEntry(form_frame, width=200)
        self.entry_unit.grid(row=1, column=3, padx=5, pady=5)

        # 成本
        ctk.CTkLabel(form_frame, text="成本：").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_cost = ctk.CTkEntry(form_frame, width=200)
        self.entry_cost.grid(row=2, column=1, padx=5, pady=5)

        # ===== 按鈕 =====
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.btn_save = ctk.CTkButton(btn_frame, text="新增原料", command=self.save_material)
        self.btn_save.grid(row=0, column=0, padx=10)

        self.btn_reset = ctk.CTkButton(btn_frame, text="重置表單", command=self.reset_form)
        self.btn_reset.grid(row=0, column=1, padx=10)

        # ===== 原料列表 =====
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "name", "brand", "spec", "unit", "cost", "stock")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        self.table.heading("id", text="ID")
        self.table.heading("name", text="名稱")
        self.table.heading("brand", text="品牌")
        self.table.heading("spec", text="規格")
        self.table.heading("unit", text="單位")
        self.table.heading("cost", text="成本")
        self.table.heading("stock", text="庫存")

        self.table.pack(fill="both", expand=True)

        # 點擊事件（用於編輯）
        self.table.bind("<Double-1>", self.on_row_double_click)

        # ===== 刪除按鈕 =====
        del_frame = ctk.CTkFrame(self)
        del_frame.pack(fill="x", padx=20, pady=10)

        self.btn_delete = ctk.CTkButton(del_frame, text="刪除選取原料", fg_color="red",
                                        command=self.delete_selected_material)
        self.btn_delete.pack()

        # 初始化表格
        self.load_material_table()

    # ---------------------------------------------------------
    # 載入原料列表
    # ---------------------------------------------------------
    def load_material_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        materials = get_all_materials()
        for m in materials:
            self.table.insert(
                "",
                "end",
                values=(
                    m["id"],
                    m["name"],
                    m["brand"] or "",
                    m["specification"] or "",
                    m["unit"],
                    m["cost"],
                    m["current_stock"],
                ),
            )

    # ---------------------------------------------------------
    # 新增 / 更新原料
    # ---------------------------------------------------------
    def save_material(self):
        name = self.entry_name.get().strip()
        brand = self.entry_brand.get().strip()
        spec = self.entry_spec.get().strip()
        unit = self.entry_unit.get().strip()
        cost = self.entry_cost.get().strip()

        if self.selected_material_id is None:
            # 新增
            ok, msg = add_material(name, brand, spec, unit, cost)
        else:
            # 修改
            ok, msg = update_material(self.selected_material_id, name, brand, spec, unit, cost)

        messagebox.showinfo("訊息", msg)

        if ok:
            self.reset_form()
            self.load_material_table()

    # ---------------------------------------------------------
    # 表單重置
    # ---------------------------------------------------------
    def reset_form(self):
        self.selected_material_id = None
        self.entry_name.delete(0, "end")
        self.entry_brand.delete(0, "end")
        self.entry_spec.delete(0, "end")
        self.entry_unit.delete(0, "end")
        self.entry_cost.delete(0, "end")

        self.btn_save.configure(text="新增原料")

    # ---------------------------------------------------------
    # 點兩下編輯資料
    # ---------------------------------------------------------
    def on_row_double_click(self, event):
        item = self.table.selection()
        if not item:
            return

        values = self.table.item(item, "values")

        self.selected_material_id = values[0]

        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, values[1])

        self.entry_brand.delete(0, "end")
        self.entry_brand.insert(0, values[2])

        self.entry_spec.delete(0, "end")
        self.entry_spec.insert(0, values[3])

        self.entry_unit.delete(0, "end")
        self.entry_unit.insert(0, values[4])

        self.entry_cost.delete(0, "end")
        self.entry_cost.insert(0, values[5])

        self.btn_save.configure(text="更新原料")

    # ---------------------------------------------------------
    # 刪除原料
    # ---------------------------------------------------------
    def delete_selected_material(self):
        item = self.table.selection()
        if not item:
            messagebox.showwarning("警告", "請先選擇一筆原料。")
            return

        material_id = self.table.item(item, "values")[0]

        ok, msg = delete_material(material_id)
        messagebox.showinfo("訊息", msg)

        if ok:
            self.load_material_table()
            self.reset_form()
