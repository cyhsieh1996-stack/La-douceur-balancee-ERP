import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from ui.theme import Color, Font, Layout
from logic.pos_import_logic import process_pos_file, get_sales_history

class PosImportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # 1. 上傳區卡片
        self.form_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.form_card.pack(fill="x", pady=(10, 10))
        self.create_upload_area()

        # 2. 歷史紀錄表格
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=8)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()
        
        self.refresh_table()

    def create_upload_area(self):
        ctk.CTkLabel(self.form_card, text="POS 報表匯入", font=Font.SUBTITLE, text_color=Color.TEXT_DARK).pack(anchor="w", padx=Layout.CARD_PADDING, pady=(10, 5))
        
        content = ctk.CTkFrame(self.form_card, fg_color="transparent")
        content.pack(fill="x", padx=Layout.CARD_PADDING, pady=(0, 10))
        
        # 說明文字
        ctk.CTkLabel(content, text="支援格式：.xlsx, .csv (需包含品名、數量、金額)", font=Font.BODY, text_color=Color.TEXT_LIGHT).pack(anchor="w", pady=(0, 10))

        # 按鈕區
        btn_box = ctk.CTkFrame(content, fg_color="transparent")
        btn_box.pack(fill="x")

        self.btn_select = ctk.CTkButton(btn_box, text="📂 選擇檔案並匯入", fg_color=Color.PRIMARY, height=38, font=Font.BODY_BOLD, command=self.handle_import)
        self.btn_select.pack(side="left")

        self.lbl_status = ctk.CTkLabel(btn_box, text="", text_color=Color.INFO, font=Font.BODY)
        self.lbl_status.pack(side="left", padx=15)

    def create_table(self):
        ctk.CTkLabel(self.table_card, text="最近匯入紀錄 (Latest 100)", font=Font.BODY_BOLD, text_color=Color.TEXT_DARK).pack(anchor="w", padx=15, pady=(10, 5))

        columns = ("date", "order", "name", "qty", "price", "amount")
        headers = ["銷售日期", "單號", "產品名稱", "數量", "單價", "總金額"]
        widths = [120, 120, 200, 60, 80, 100]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")

        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rows = get_sales_history()
        for i, row in enumerate(rows):
            # row: date, order_id, product_name, qty, price, amount
            try: 
                qty = int(row[3]) if float(row[3]).is_integer() else row[3]
                amt = int(row[5])
            except: 
                qty, amt = row[3], row[5]
                
            values = (row[0], row[1], row[2], qty, row[4], amt)
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def handle_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")])
        if not file_path: return
        
        self.lbl_status.configure(text="處理中...", text_color=Color.WARNING)
        self.update_idletasks() # 強制刷新 UI
        
        success, msg = process_pos_file(file_path)
        
        if success:
            self.lbl_status.configure(text=msg, text_color=Color.SUCCESS)
            messagebox.showinfo("成功", msg)
            self.refresh_table()
        else:
            self.lbl_status.configure(text="匯入失敗", text_color=Color.DANGER)
            messagebox.showerror("錯誤", msg)