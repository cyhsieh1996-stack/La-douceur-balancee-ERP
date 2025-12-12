import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from ui.theme import Color, Font, Layout
from logic.pos_import_logic import preview_pos_sales, confirm_sales_deduction

class POSImportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.preview_data = [] 

        # 1. 頂部操作區 (白色卡片)
        self.top_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.top_card.pack(fill="x", pady=(20, 15))
        
        # 設定 Grid 權重
        self.top_card.columnconfigure(1, weight=1)
        
        # ⚠️ 修改文字：明確指出需要 iCHEF 商品銷售分析報表
        ctk.CTkLabel(self.top_card, text="匯入 iCHEF 商品銷售分析報表：", font=Font.BODY, text_color=Color.TEXT_DARK).grid(row=0, column=0, padx=(20, 10), pady=20, sticky="w")
        
        # 檔名顯示欄位
        self.entry_filename = ctk.CTkEntry(self.top_card, placeholder_text="尚未選擇檔案", state="readonly")
        self.entry_filename.grid(row=0, column=1, padx=10, sticky="ew")
        
        # 📂 藍色按鈕：選擇檔案
        self.btn_select = ctk.CTkButton(
            self.top_card, 
            text="📂 選擇檔案", 
            fg_color=Color.PRIMARY, 
            width=120, 
            height=35, 
            command=self.select_file
        )
        self.btn_select.grid(row=0, column=2, padx=10)

        # ✅ 綠色按鈕：確認扣除
        self.btn_confirm = ctk.CTkButton(
            self.top_card, 
            text="✅ 確認扣除", 
            fg_color=Color.SUCCESS,
            hover_color="#148F77", 
            width=120, 
            height=35, 
            state="disabled", 
            command=self.confirm_import
        )
        self.btn_confirm.grid(row=0, column=3, padx=(0, 20))

        # 2. 預覽表格區
        self.table_card = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        self.create_table()

    def create_table(self):
        columns = ("name", "sales", "current", "after", "status")
        headers = ["產品名稱", "銷售數量", "目前庫存", "預計剩餘", "狀態"]
        widths = [250, 100, 100, 100, 150]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=Color.TEXT_DARK, rowheight=Color.TABLE_ROW_HEIGHT, font=Font.SMALL, fieldbackground="white", borderwidth=0)
        style.configure("Treeview.Heading", font=Font.TABLE_HEADER, background=Color.TABLE_HEADER_BG, foreground=Color.TEXT_DARK, relief="flat")
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings")
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center")
        
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background=Color.TABLE_ROW_ALT)
        
        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="選擇銷售報表", filetypes=[("Excel/CSV Files", "*.csv *.xlsx")])
        if not file_path: return
        
        self.entry_filename.configure(state="normal")
        self.entry_filename.delete(0, "end")
        self.entry_filename.insert(0, file_path.split("/")[-1])
        self.entry_filename.configure(state="readonly")
        
        success, result = preview_pos_sales(file_path)
        if not success: 
            messagebox.showerror("錯誤", result)
            return
            
        self.preview_data = result
        self.refresh_table()
        
        if self.preview_data: 
            self.btn_confirm.configure(state="normal")
        else: 
            self.btn_confirm.configure(state="disabled")
            messagebox.showinfo("提示", "檔案中沒有讀取到有效銷售資料，請確認是否為 iCHEF 商品銷售分析報表。")

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, row in enumerate(self.preview_data):
            values = (row['name'], row['sales_qty'], row['current_stock'], row['stock_after'], row['status'])
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))

    def confirm_import(self):
        if not self.preview_data: return
        if not messagebox.askyesno("確認", "確定要執行扣庫存嗎？\n此動作將無法復原。"): return
        
        success, msg = confirm_sales_deduction(self.preview_data)
        if success:
            messagebox.showinfo("成功", msg)
            self.preview_data = []
            self.refresh_table()
            self.entry_filename.configure(state="normal")
            self.entry_filename.delete(0, "end")
            self.entry_filename.configure(state="readonly")
            self.btn_confirm.configure(state="disabled")
        else:
            messagebox.showerror("失敗", msg)