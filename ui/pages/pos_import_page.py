import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from ui.theme import Color, Font
from logic.pos_import_logic import preview_pos_sales, confirm_sales_deduction

class POSImportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.preview_data = [] # 暫存預覽資料

        # 1. 標題
        title = ctk.CTkLabel(
            self, 
            text="POS 銷售匯入 Sales Import", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 15))

        # 2. 檔案選擇區 (卡片)
        self.top_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.top_card.pack(fill="x", pady=(0, 15))
        
        btn_frame = ctk.CTkFrame(self.top_card, fg_color="transparent")
        btn_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(btn_frame, text="請選擇 POS 匯出的銷售報表 (Excel/CSV)：", font=Font.BODY, text_color=Color.TEXT_DARK).pack(side="left")
        
        self.btn_select = ctk.CTkButton(
            btn_frame, 
            text="📂 選擇檔案...", 
            command=self.select_file,
            font=Font.BODY
        )
        self.btn_select.pack(side="left", padx=10)
        
        self.lbl_filename = ctk.CTkLabel(btn_frame, text="尚未選擇檔案", text_color=Color.TEXT_LIGHT)
        self.lbl_filename.pack(side="left", padx=10)

        # 3. 預覽表格 (卡片)
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        
        self.create_table()

        # 4. 底部動作區
        self.action_frame = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=20)
        
        self.btn_confirm = ctk.CTkButton(
            self.action_frame, 
            text="✅ 確認扣除庫存", 
            fg_color="#2CC985", 
            hover_color="#25A970",
            font=("Microsoft JhengHei UI", 16, "bold"),
            height=45,
            state="disabled", # 預設停用，直到有預覽資料
            command=self.confirm_import
        )
        self.btn_confirm.pack(fill="x")

    def create_table(self):
        columns = ("name", "sales", "current", "after", "status")
        headers = ["產品名稱", "銷售數量", "目前庫存", "預計剩餘", "狀態"]
        widths = [250, 100, 100, 100, 150]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=30, font=Font.SMALL)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background="#F0F0F0", foreground=Color.TEXT_DARK)
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇銷售報表",
            filetypes=[("Excel/CSV Files", "*.csv *.xlsx")]
        )
        
        if not file_path:
            return
            
        self.lbl_filename.configure(text=file_path.split("/")[-1])
        
        # 執行預覽邏輯
        success, result = preview_pos_sales(file_path)
        
        if not success:
            messagebox.showerror("錯誤", result)
            return
            
        self.preview_data = result
        self.refresh_table()
        
        # 如果有資料，啟用確認按鈕
        if self.preview_data:
            self.btn_confirm.configure(state="normal")
        else:
            self.btn_confirm.configure(state="disabled")
            messagebox.showinfo("提示", "檔案中沒有讀取到有效銷售資料")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in self.preview_data:
            values = (
                row['name'], 
                row['sales_qty'], 
                row['current_stock'], 
                row['stock_after'], 
                row['status']
            )
            # 如果狀態不是「正常」，標示一下顏色 (這裡僅示範邏輯，Treeview 上色比較複雜，先顯示文字即可)
            self.tree.insert("", "end", values=values)

    def confirm_import(self):
        if not self.preview_data: return
        
        confirm = messagebox.askyesno("確認", "確定要執行扣庫存嗎？\n此動作將無法復原。")
        if not confirm: return
        
        success, msg = confirm_sales_deduction(self.preview_data)
        
        if success:
            messagebox.showinfo("成功", msg)
            # 清空畫面
            self.preview_data = []
            self.refresh_table()
            self.lbl_filename.configure(text="尚未選擇檔案")
            self.btn_confirm.configure(state="disabled")
        else:
            messagebox.showerror("失敗", msg)