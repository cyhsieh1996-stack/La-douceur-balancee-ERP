import customtkinter as ctk
from tkinter import messagebox
from logic.raw_materials_logic import (
    get_all_raw_materials,
    add_new_raw_material,
    save_multiple_raw_materials,
)

# ---------------------------------------------------
# 原料分類（代碼 + 中文名稱）
# ---------------------------------------------------
RAW_MATERIAL_CATEGORIES = {
    "SU": "糖類",
    "FL": "粉類（麵粉/澱粉）",
    "DA": "乳製品",
    "EG": "蛋類",
    "CH": "巧克力 / 可可",
    "FR": "水果類",
    "NT": "堅果",
    "SP": "香料 / 抹茶 / 茶葉",
    "OI": "油脂",
    "OT": "其他",
}

CATEGORY_DROPDOWN = [f"{k} – {v}" for k, v in RAW_MATERIAL_CATEGORIES.items()] + ["CUSTOM（自訂分類）"]

UNIT_OPTIONS = ["g", "kg", "ml", "L", "顆", "個", "包", "袋", "箱", "瓶", "罐"]


# ===================================================
# 新增/編輯 原料對話框
# ===================================================
class RawMaterialDialog(ctk.CTkToplevel):

    def __init__(self, master, title, material=None):
        super().__init__(master)
        self.title(title)
        self.geometry("420x480")
        self.resizable(False, False)
        self.material = material
        self.result = None

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # 名稱
        ctk.CTkLabel(form, text="原料名稱：").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ctk.CTkEntry(form, width=260)
        self.entry_name.grid(row=0, column=1, padx=10, pady=5)

        # 類別（下拉 + custom）
        ctk.CTkLabel(form, text="類別：").grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = ctk.StringVar()
        self.category_dropdown = ctk.CTkComboBox(
            form,
            values=CATEGORY_DROPDOWN,
            variable=self.category_var,
            width=260,
            command=self._category_changed
        )
        self.category_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # 自訂分類（隱藏）
        self.custom_category_entry = ctk.CTkEntry(form, width=260)
        self.custom_category_entry.grid(row=2, column=1, padx=10, pady=5)
        self.custom_category_entry.grid_remove()

        ctk.CTkLabel(form, text="").grid(row=2, column=0)

        # 單位
        ctk.CTkLabel(form, text="單位：").grid(row=3, column=0, sticky="w", pady=5)
        self.unit_var = ctk.StringVar()
        self.unit_dropdown = ctk.CTkComboBox(form, values=UNIT_OPTIONS, variable=self.unit_var, width=260)
        self.unit_dropdown.grid(row=3, column=1, padx=10, pady=5)

        # 備註
        ctk.CTkLabel(form, text="備註：").grid(row=4, column=0, sticky="nw", pady=5)
        self.entry_notes = ctk.CTkEntry(form, width=260)
        self.entry_notes.grid(row=4, column=1, padx=10, pady=5)

        # 成本
        ctk.CTkLabel(form, text="成本（可空白）：").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_cost = ctk.CTkEntry(form, width=260)
        self.entry_cost.grid(row=5, column=1, padx=10, pady=5)

        # 追蹤庫存
        ctk.CTkLabel(form, text="追蹤庫存：").grid(row=6, column=0, sticky="w", pady=5)
        self.track_var = ctk.BooleanVar(value=True)
        self.track_check = ctk.CTkCheckBox(form, variable=self.track_var, text="")
        self.track_check.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        # 底部按鈕
        btn_bar = ctk.CTkFrame(self)
        btn_bar.pack(pady=10)

        ctk.CTkButton(btn_bar, text="取消", command=self.destroy, width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_bar, text="儲存", command=self._submit, width=120).pack(side="left", padx=10)

        # 編輯模式填資料
        if material:
            self._fill_material()

    # ------------------------------------------------
    def _fill_material(self):
        m = self.material
        self.entry_name.insert(0, m["name"])

        # 分類
        if m["category"] in RAW_MATERIAL_CATEGORIES:
            self.category_dropdown.set(f"{m['category']} – {RAW_MATERIAL_CATEGORIES[m['category']]}")
        else:
            self.category_dropdown.set("CUSTOM（自訂分類）")
            self.custom_category_entry.grid()
            self.custom_category_entry.insert(0, m["category"])

        self.unit_dropdown.set(m["unit"])

        if m.get("notes"):
            self.entry_notes.insert(0, m["notes"])

        if m.get("cost") is not None:
            self.entry_cost.insert(0, str(m["cost"]))

        self.track_var.set(bool(m["track_stock"]))

    # ------------------------------------------------
    def _category_changed(self, value):
        if value.startswith("CUSTOM"):
            self.custom_category_entry.grid()
        else:
            self.custom_category_entry.grid_remove()

    # ------------------------------------------------
    def _submit(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("錯誤", "原料名稱不可空白")
            return

        # 分類
        raw_cat = self.category_var.get()
        if raw_cat.startswith("CUSTOM"):
            category = self.custom_category_entry.get().strip()
            if not category:
                messagebox.showerror("錯誤", "請輸入自訂分類")
                return
        else:
            category = raw_cat.split(" – ")[0]

        unit = self.unit_var.get()
        notes = self.entry_notes.get().strip()

        cost_raw = self.entry_cost.get().strip()
        cost = float(cost_raw) if cost_raw else None

        track = 1 if self.track_var.get() else 0

        self.result = {
            "name": name,
            "category": category,
            "unit": unit,
            "notes": notes,
            "cost": cost,
            "track_stock": track,
        }

        self.destroy()


# ===================================================
# 主頁：原料管理
# ===================================================
class RawMaterialsPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="原料管理", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        self.materials = get_all_raw_materials()
        self.modified_rows = {}

        # 表格
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._draw_table()

        # 底部按鈕
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", pady=10)

        ctk.CTkButton(bottom, text="新增原料", command=self._open_add_dialog, width=160).pack(side="left", padx=20)
        ctk.CTkButton(bottom, text="全部儲存", command=self._save_changes, width=160).pack(side="right", padx=20)

    # ------------------------------------------------
    def _draw_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["ID", "名稱", "分類", "單位", "備註", "成本", "追蹤", "編輯"]

        for col, h in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=h, font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=col, padx=6, pady=4
            )

        for r, m in enumerate(self.materials, start=1):

            ctk.CTkLabel(self.table_frame, text=m["item_id"], width=80).grid(row=r, column=0)

            ctk.CTkLabel(self.table_frame, text=m["name"], width=150).grid(row=r, column=1)

            # 分類只顯示代碼
            ctk.CTkLabel(self.table_frame, text=m["category"], width=70).grid(row=r, column=2)

            ctk.CTkLabel(self.table_frame, text=m["unit"], width=50).grid(row=r, column=3)

            ctk.CTkLabel(self.table_frame, text=m.get("notes", "")).grid(row=r, column=4)

            ctk.CTkLabel(self.table_frame, text=m.get("cost", "")).grid(row=r, column=5)

            ctk.CTkLabel(self.table_frame, text="✓" if m["track_stock"] else "✕").grid(row=r, column=6)

            ctk.CTkButton(
                self.table_frame,
                text="編輯",
                width=60,
                command=lambda mm=m: self._open_edit_dialog(mm),
            ).grid(row=r, column=7, padx=4)

    # ------------------------------------------------
    def _open_edit_dialog(self, material):
        dlg = RawMaterialDialog(self, "編輯原料", material)
        self.wait_window(dlg)

        if dlg.result:
            self.modified_rows[material["item_id"]] = dlg.result
            messagebox.showinfo("暫存成功", f"{material['item_id']} 已暫存修改")

    # ------------------------------------------------
    def _open_add_dialog(self):
        dlg = RawMaterialDialog(self, "新增原料")
        self.wait_window(dlg)

        if dlg.result:
            new_id = add_new_raw_material(dlg.result)
            messagebox.showinfo("成功", f"原料已新增：{new_id}")

            self.materials = get_all_raw_materials()
            self._draw_table()

    # ------------------------------------------------
    def _save_changes(self):
        if not self.modified_rows:
            messagebox.showinfo("訊息", "沒有需要儲存的變更")
            return

        save_multiple_raw_materials(self.modified_rows)
        messagebox.showinfo("成功", "所有修改已儲存")

        self.modified_rows = {}
        self.materials = get_all_raw_materials()
        self._draw_table()
