import customtkinter as ctk
from tkinter import ttk, messagebox

from logic.raw_materials_logic import (
    get_all_materials,
    add_material,
    update_material,
    delete_material,
)


class RawMaterialsPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="原料管理",
                              font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        # 表單區
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=10)

        labels = ["原料名稱", "廠牌", "規格", "最小單位", "安全庫存"]
        self.entries = []

        for i, label in enumerate(labels):
            ctk.CTkLabel(form, text=label).grid(
                row=i, column=0, padx=5, pady=5, sticky="e")

            entry = ctk.CTkEntry(form, width=220)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(entry)

        add_btn = ctk.CTkButton(form, text="新增原料", command=self.add_material)
        add_btn.grid(row=5, column=0, columnspan=2, pady=15)

        # 表格區
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20)

        columns = ("id", "name", "brand", "spec",
                   "unit", "safe_stock", "current_stock")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.table.heading(col, text=col)

        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self.on_edit)

        self.load_data()

    # --------------------------------------------------
    # 載入原料列表
    # --------------------------------------------------
    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        materials = get_all_materials()

        for m in materials:
            self.table.insert(
                "",
                "end",
                values=(
                    m["id"], m["name"], m["brand"], m["spec"],
                    m["unit"], m["safe_stock"], m["current_stock"]
                )
            )

    # --------------------------------------------------
    # 新增原料
    # --------------------------------------------------
    def add_material(self):
        vals = [e.get() for e in self.entries]
        if not vals[0]:
            messagebox.showerror("錯誤", "原料名稱不可空白")
            return

        ok, msg = add_material(*vals)
        messagebox.showinfo("訊息", msg)
        self.load_data()

    # --------------------------------------------------
    # 編輯原料（雙擊）
    # --------------------------------------------------
    def on_edit(self, event):
        selected = self.table.focus()
        if not selected:
            return

        values = self.table.item(selected, "values")
        mat_id = values[0]

        edit_win = ctk.CTkToplevel(self)
        edit_win.title("編輯原料")
        edit_win.geometry("400x350")

        fields = ["名稱", "廠牌", "規格", "最小單位", "安全庫存"]
        entries = []

        for i, f in enumerate(fields):
            ctk.CTkLabel(edit_win, text=f).pack(pady=5)
            entry = ctk.CTkEntry(edit_win)
            entry.insert(0, values[i+1])
            entry.pack(pady=5)
            entries.append(entry)

        def save_edit():
            data = [e.get() for e in entries]
            ok, msg = update_material(
                mat_id, data[0], data[1], data[2], data[3], data[4])
            messagebox.showinfo("訊息", msg)
            edit_win.destroy()
            self.load_data()

        def do_delete():
            ok, msg = delete_material(mat_id)
            messagebox.showinfo("訊息", msg)
            edit_win.destroy()
            self.load_data()

        ctk.CTkButton(edit_win, text="儲存變更", command=save_edit).pack(pady=10)
        ctk.CTkButton(edit_win, text="刪除此原料", fg_color="red",
                      command=do_delete).pack(pady=5)
