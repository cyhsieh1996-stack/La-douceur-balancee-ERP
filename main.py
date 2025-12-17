import customtkinter as ctk
from ui.theme import Color
from ui.sidebar import Sidebar
from ui.pages.dashboard_page import DashboardPage
from ui.pages.raw_materials_page import RawMaterialsPage
from ui.pages.products_page import ProductsPage
from ui.pages.inbound_page import InboundPage
from ui.pages.production_page import ProductionPage
from ui.pages.pos_import_page import PosImportPage
from ui.pages.inventory_page import InventoryPage
from database.db import init_db
# ⚠️ 新增備份邏輯
from logic.backup_logic import perform_backup 

class SweetERPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("La Douceur Balancée - 甜點ERP系統")
        self.geometry("1200x800")
        ctk.set_appearance_mode("Light")
        
        # 初始化資料庫
        init_db()
        
        # ⚠️ 啟動時執行自動備份
        self.run_auto_backup()

        # 版面配置 (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. 側邊欄
        self.sidebar = Sidebar(self, command=self.switch_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. 主內容區
        self.main_area = ctk.CTkFrame(self, fg_color=Color.MAIN_BG, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        # 頁面快取
        self.pages = {}
        self.current_page = None

        # 預設顯示首頁
        self.switch_page("dashboard")

    def run_auto_backup(self):
        # 在背景執行備份，不卡住介面
        success, msg = perform_backup()
        if not success:
            print(f"備份警告: {msg}")

    def switch_page(self, page_name):
        # 清除舊頁面
        if self.current_page:
            self.current_page.pack_forget()

        # 懶加載 (Lazy Loading)
        if page_name not in self.pages:
            if page_name == "dashboard":
                self.pages[page_name] = DashboardPage(self.main_area)
            elif page_name == "raw_materials":
                self.pages[page_name] = RawMaterialsPage(self.main_area)
            elif page_name == "products":
                self.pages[page_name] = ProductsPage(self.main_area)
            elif page_name == "inbound":
                self.pages[page_name] = InboundPage(self.main_area)
            elif page_name == "production":
                self.pages[page_name] = ProductionPage(self.main_area)
            elif page_name == "pos_import":
                self.pages[page_name] = PosImportPage(self.main_area)
            elif page_name == "inventory":
                self.pages[page_name] = InventoryPage(self.main_area)

        # 顯示新頁面
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True, padx=20, pady=20)

if __name__ == "__main__":
    app = SweetERPApp()
    app.mainloop()