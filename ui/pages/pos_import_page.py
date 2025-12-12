import customtkinter as ctk
from tkinter import filedialog, messagebox

from logic.pos_logic import import_pos_csv


class POSImportPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="POS 資料匯入",
                             font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(pady=20)

        info = ctk.CTkLabel(self, text="請選擇 POS 銷售紀錄 CSV 檔案匯入",
                            font=ctk.CTkFont(size=16))
        info.pack(pady=10)

        ctk.CTkButton(self, text="選擇 CSV 檔案",
                      command=self.pick_file).pack(pady=15)

    def pick_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

        if not path:
            return

        ok, msg = import_pos_csv(path)
        messagebox.showinfo("完成", msg)
