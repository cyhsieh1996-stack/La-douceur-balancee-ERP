import customtkinter as ctk

# 測試原料資料（未串 DB 前）
TEST_MATERIALS = [
    {"id": 1, "code": "A001", "name": "雞蛋", "brand": "福樂", "vendor": "大宗食品", "spec": "12入/盒", "unit": "顆"},
    {"id": 2, "code": "A002", "name": "砂糖", "brand": "台糖", "vendor": "台糖公司", "spec": "1kg/包", "unit": "kg"},
    {"id": 3, "code": "A003", "name": "奶油", "brand": "安佳", "vendor": "進口商", "spec": "454g/塊", "unit": "g"},
]


class MaterialPage(ctk.CTkFrame):
    """原料資料管理（customtkinter 版本）"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="#F7F4EF")

        self.materials = TEST_MATERIALS.copy()

        # ======= 標題區 =======
        title = ctk.CTkLabel(
            self,
            text="📦 原料清單",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#4A4A48",
        )
        title.pack(anchor="w", padx=25, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="管理所有原料的基本資訊、供應商與規格",
            font=ctk.CTkFont(size=15),
            text_color="#6B6B6A",
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))

        # ======= 按鈕列 =======
        btn_row = ctk.CTkFrame(self, fg_color="#EFECE7", corner_radius=12)
        btn_row.pack(fill="x", padx=25, pady=(0, 20))

        add_btn = ctk.CTkButton(btn_row, text="＋ 新增原料", command=self.open_add_dialog)
        add_btn.pack(side="left", padx=10, pady=12)

        refresh_btn = ctk.CTkButton(btn_row, text="重新整理", command=self.render_list)
        refresh_btn.pack(side="left", padx=10, pady=12)

        # ======= 捲動清單 =======
        list_container = ctk.CTkFrame(self, fg_color="#EFECE7", corner_radius=12)
        list_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        self.scroll_area = ctk.CTkScrollableFrame(list_container, fg_color="#F7F4EF")
        self.scroll_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.row_widgets = []
        self.render_list()

    # ---------------------------------------------------------
    # 顯示列表
    # ---------------------------------------------------------
    def render_list(self):
        for w in self.row_widgets:
            w.destroy()
        self.row_widgets.clear()

        if not self.materials:
            lbl = ctk.CTkLabel(
                self.scroll_area,
                text="尚無原料資料。",
                text_color="#4A4A48",
                font=ctk.CTkFont(size=15),
            )
            lbl.pack(pady=10)
            self.row_widgets.append(lbl)
            return

        for m in self.materials:
            row = self._make_row(m)
            row.pack(fill="x", padx=5, pady=4)
            self.row_widgets.append(row)

    # ---------------------------------------------------------
    # 單列 UI
    # ---------------------------------------------------------
    def _make_row(self, m):
        row = ctk.CTkFrame(self.scroll_area, fg_color="#EFECE7", corner_radius=10)

        text = (
            f"{m['code']} ｜ {m['name']}（品牌: {m['brand']}） | "
            f"供應商: {m['vendor']} | 規格: {m['spec']} | 單位: {m['unit']}"
        )

        lbl = ctk.CTkLabel(
            row,
            text=text,
            text_color="#4A4A48",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        lbl.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        edit_btn = ctk.CTkButton(
            row, text="編輯", width=60, command=lambda mid=m["id"]: self.open_edit_dialog(mid)
        )
        edit_btn.pack(side="right", padx=5, pady=10)

        del_btn = ctk.CTkButton(
            row,
            text="刪除",
            width=60,
            fg_color="#C95C54",
            hover_color="#B94A42",
            command=lambda mid=m["id"]: self.delete_material(mid),
        )
        del_btn.pack(side="right", padx=5, pady=10)

        return row

    # ---------------------------------------------------------
    # CRUD function
    # ---------------------------------------------------------
    def delete_material(self, mid):
        self.materials = [m for m in self.materials if m["id"] != mid]
        self.render_list()

    def add_material(self, data):
        new_id = max([m["id"] for m in self.materials]) + 1 if self.materials else 1
        data["id"] = new_id
        self.materials.append(data)
        self.render_list()

    def update_material(self, mid, newdata):
        for m in self.materials:
            if m["id"] == mid:
                m.update(newdata)
        self.render_list()

    # ---------------------------------------------------------
    # Dialogs
    # ---------------------------------------------------------
    def open_add_dialog(self):
        MaterialDialog(
            parent=self,
            title="新增原料",
            on_confirm=self.add_material,
        )

    def open_edit_dialog(self, mid):
        data = next((m for m in self.materials if m["id"] == mid), None)
        if data:
            MaterialDialog(
                parent=self,
                title="編輯原料",
                data=data,
                on_confirm=lambda newdata: self.update_material(mid, newdata),
            )


# ===============================
# 編輯 / 新增 Dialog
# ===============================
class MaterialDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, on_confirm, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("430x520")
        self.on_confirm = on_confirm

        self.lift()
        self.grab_set()
        self.configure(fg_color="#F7F4EF")

        form = ctk.CTkFrame(self, fg_color="#EFECE7", corner_radius=12)
        form.pack(fill="both", expand=True, padx=20, pady=20)

        labels = ["編號", "品名", "品牌", "供應商", "規格", "單位"]
        keys = ["code", "name", "brand", "vendor", "spec", "unit"]

        self.entries = {}
        for label, key in zip(labels, keys):
            ctk.CTkLabel(form, text=label, text_color="#4A4A48").pack(anchor="w", padx=10)
            entry = ctk.CTkEntry(form, placeholder_text=f"輸入{label}")
            entry.pack(fill="x", padx=10, pady=(0, 10))
            self.entries[key] = entry

        if data:
            for k in keys:
                self.entries[k].insert(0, data.get(k, ""))

        btn_row = ctk.CTkFrame(form)
        btn_row.pack(pady=10)

        ok_btn = ctk.CTkButton(btn_row, text="確定", command=self.submit)
        ok_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(btn_row, text="取消", fg_color="#AAA", command=self.destroy)
        cancel_btn.pack(side="left", padx=8)

    def submit(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        self.on_confirm(data)
        self.destroy()
