import customtkinter as ctk
from datetime import date

from logic.monthly_adjust_logic import (
    record_adjustment,
    list_adjustments,
    get_system_inventory_dict,
    list_items,
)


class MonthlyAdjustPage(ctk.CTkFrame):
    """月結盤點調整"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="#F7F4EF")

        title = ctk.CTkLabel(
            self,
            text="📊 月結盤點調整（Monthly Adjustment）",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#4A4A48",
        )
        title.pack(anchor="w", padx=25, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="輸入實際盤點數據，系統自動生成調整出入庫紀錄",
            font=ctk.CTkFont(size=15),
            text_color="#6B6B6A",
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))

        container = ctk.CTkFrame(self, fg_color="#EFECE7", corner_radius=12)
        container.pack(fill="both", expand=True, padx=25, pady=20)

        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------------------
        # 上方區塊：新增盤點
        # ---------------------------------------------------------
        form = ctk.CTkFrame(container, fg_color="#F7F4EF", corner_radius=12)
        form.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkLabel(
            form,
            text="新增盤點紀錄",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A4A48",
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5))

        # 原料+成品皆可盤點
        items = list_items()
        self.item_map = {f'{i["id"]} - {i["name"]}': str(i["id"]) for i in items}
        self.item_labels = list(self.item_map.keys())

        ctk.CTkLabel(form, text="品項：", text_color="#4A4A48").grid(
            row=1, column=0, sticky="w", padx=15, pady=5
        )
        self.item_combo = ctk.CTkComboBox(form, values=self.item_labels)
        self.item_combo.grid(row=1, column=1, sticky="ew", padx=15, pady=5)
        if self.item_labels:
            self.item_combo.set(self.item_labels[0])

        # 帳面數量（自動帶出）
        ctk.CTkLabel(form, text="帳面庫存：", text_color="#4A4A48").grid(
            row=2, column=0, sticky="w", padx=15, pady=5
        )
        self.system_entry = ctk.CTkEntry(form)
        self.system_entry.grid(row=2, column=1, sticky="ew", padx=15, pady=5)

        # 實際數量
        ctk.CTkLabel(form, text="實際庫存：", text_color="#4A4A48").grid(
            row=3, column=0, sticky="w", padx=15, pady=5
        )
        self.physical_entry = ctk.CTkEntry(form)
        self.physical_entry.grid(row=3, column=1, sticky="ew", padx=15, pady=5)

        # 按鈕：套用盤點
        ctk.CTkButton(
            form,
            text="＋ 套用調整",
            command=self.apply_adjustment
        ).grid(row=4, column=1, sticky="e", padx=15, pady=(10, 15))

        # ---------------------------------------------------------
        # 下方區塊：盤點歷史
        # ---------------------------------------------------------
        history = ctk.CTkFrame(container, fg_color="#F7F4EF", corner_radius=12)
        history.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        ctk.CTkLabel(
            history,
            text="盤點紀錄",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A4A48",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.scroll = ctk.CTkScrollableFrame(history, fg_color="#EFECE7")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=12)

        self.render_history()

        # 自動載入帳面庫存
        self.bind_item_selection()

    # ---------------------------------------------------------
    # 帶出帳面庫存
    # ---------------------------------------------------------
    def bind_item_selection(self):
        inventory = get_system_inventory_dict()

        def update_system_qty(choice):
            item_label = self.item_combo.get().strip()
            item_id = self.item_map.get(item_label, "")
            qty = inventory.get(item_id, 0)
            self.system_entry.delete(0, "end")
            self.system_entry.insert(0, str(qty))

        # 綁定 combobox
        self.item_combo.configure(command=update_system_qty)

    # ---------------------------------------------------------
    # 套用調整
    # ---------------------------------------------------------
    def apply_adjustment(self):
        item_label = self.item_combo.get().strip()
        item_id = self.item_map.get(item_label)
        if not item_id:
            return
        system_qty = float(self.system_entry.get().strip() or "0")
        physical_qty = float(self.physical_entry.get().strip() or "0")

        today = str(date.today())

        record_adjustment(today, item_id, system_qty, physical_qty)

        self.system_entry.delete(0, "end")
        self.physical_entry.delete(0, "end")

        self.render_history()

    # ---------------------------------------------------------
    # 顯示歷史調整
    # ---------------------------------------------------------
    def render_history(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        records = list_adjustments()

        if not records:
            ctk.CTkLabel(self.scroll, text="尚無盤點紀錄", text_color="#4A4A48").pack(pady=10)
            return

        for r in records:
            row = ctk.CTkFrame(self.scroll, fg_color="#F7F4EF", corner_radius=10)
            row.pack(fill="x", padx=8, pady=5)

            text = (
                f"{r['date']}｜{r['item_id']} {r['item_name']}｜"
                f"帳面 {r['system_qty']} → 實際 {r['physical_qty']}｜"
                f"差異 {r['diff']} {r['unit']}"
            )

            ctk.CTkLabel(row, text=text, text_color="#4A4A48").pack(
                anchor="w", padx=12, pady=10
            )
