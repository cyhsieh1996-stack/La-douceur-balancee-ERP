import customtkinter as ctk
from ui.theme import Color, Font
# 確保您已經建立了這個邏輯檔案
from logic.materials_logic import add_material, update_material 

class MaterialItemWindow(ctk.CTkToplevel):
    def __init__(self, parent, edit_data=None, on_close_callback=None):
        super().__init__(parent)
        self.edit_data = edit_data
        self.on_close_callback = on_close_callback
        
        title = "編輯原料" if edit_data else "新增原料"
        self.title(title)
        self.geometry("500x650")
        
        # 設定視窗置頂
        self.attributes("-topmost", True)
        
        # 主要容器
        self.frame = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 標題
        ctk.CTkLabel(self.frame, text=title, font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(pady=(20, 20))

        # --- 表單區 ---
        self.entries = {}
        
        # 定義欄位 (Label 文字, 變數名稱)
        fields = [
            ("原料名稱", "name"),
            ("類別", "category"),
            ("廠牌", "brand"),
            ("廠商", "vendor"),
            ("單位", "unit"),
            ("安全庫存", "safe_stock"),
        ]

        for label_text, field_name in fields:
            row = ctk.CTkFrame(self.frame, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=5)
            
            ctk.CTkLabel(row, text=label_text, width=80, anchor="w", font=Font.BODY, text_color=Color.TEXT_DARK).pack(side="left")
            
            entry = ctk.CTkEntry(row, height=35)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[field_name] = entry

        # --- 按鈕區 ---
        btn_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_row.pack(pady=30)

        ctk.CTkButton(btn_row, text="儲存", fg_color=Color.PRIMARY, width=120, height=40, command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="取消", fg_color=Color.GRAY_BUTTON, text_color=Color.TEXT_DARK, hover_color=Color.GRAY_BUTTON_HOVER, width=120, height=40, command=self.destroy).pack(side="left", padx=10)

        # 如果是編輯模式，載入舊資料
        if self.edit_data:
            self.load_data()

    def load_data(self):
        d = self.edit_data
        # 依序填入資料，若無資料則留空
        for field, entry in self.entries.items():
            val = d.get(field, "")
            if val is None: val = ""
            entry.insert(0, str(val))

    def save(self):
        # 收集表單資料
        data = {field: entry.get() for field, entry in self.entries.items()}

        # 簡易驗證：名稱必填
        if not data["name"]:
            # 這裡可以加一個錯誤提示彈窗，或直接 return
            print("錯誤：原料名稱為必填")
            return

        try:
            data["safe_stock"] = float(data["safe_stock"]) if data["safe_stock"] else 0
        except ValueError:
            print("錯誤：安全庫存必須是數字")
            return

        if self.edit_data:
            # 更新
            success, msg = update_material(self.edit_data["id"], data)
        else:
            # 新增
            success, msg = add_material(data)

        if success:
            if self.on_close_callback:
                self.on_close_callback() # 通知上一頁刷新
            self.destroy()
        else:
            print(f"儲存失敗: {msg}")
