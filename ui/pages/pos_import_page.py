import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from logic.pos_import_logic import import_pos_weekly_data

class POSImportPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        ctk.CTkLabel(self, text="POS Weekly 資料匯入", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # 顯示選取檔案
        self.file_path_var = ctk.StringVar(value="尚未選擇檔案")
        ctk.CTkLabel(self, textvariable=self.file_path_var, wraplength=600).pack(pady=10)

        # 選擇 CSV 按鈕
        ctk.CTkButton(self, text="選擇 iCHEF weekly CSV 檔案", command=self.select_file).pack(pady=10)

        # 匯入按鈕
        ctk.CTkButton(self, text="開始匯入", fg_color="#3B82F6", command=self.import_data).pack(pady=20)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def import_data(self):
        file_path = self.file_path_var.get()
        if file_path == "尚未選擇檔案":
            messagebox.showerror("錯誤", "請先選擇要匯入的 CSV 檔案")
            return

        try:
            result = import_pos_weekly_data(file_path)

            messagebox.showinfo(
                "匯入成功",
                f"已成功匯入 POS 每週資料！\n\n"
                f"週期：{result['week_range']}\n"
                f"營收：{result['total_sales']}\n"
                f"銷量：{result['total_qty']}\n"
                f"品項數：{result['items_count']}\n"
            )

        except Exception as e:
            messagebox.showerror("匯入失敗", f"匯入時發生錯誤：\n{e}")
