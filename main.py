# main.py
import customtkinter as ctk

# 匯入所有頁面
from ui.pages.dashboard_page import DashboardPage
from ui.pages.raw_materials_page import RawMaterialsPage
from ui.pages.inbound_page import InboundPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.products_page import ProductsPage
from ui.pages.recipes_page import RecipesPage
from ui.pages.production_page import ProductionPage
from ui.pages.pos_import_page import POSImportPage


# --------------------------------------------------
# 主視窗
# --------------------------------------------------
class SweetERPMainApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SweetERP - 甘味平橫 ERP")
        self.geometry("1200x750")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 左側選單列
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(self, corner_radius=10)
        self.main_area.pack(side="right", fill="both", expand=True)

        # 建立按鈕
        self.create_sidebar_buttons()

        # 預設頁面：儀表板
        self.show_page(DashboardPage)

    # --------------------------------------------------
    # 建立左側選單
    # --------------------------------------------------
    def create_sidebar_buttons(self):
        buttons = [
            ("儀表板 Dashboard", DashboardPage),
            ("原料管理 Raw Materials", RawMaterialsPage),
            ("原料入庫 Inbound", InboundPage),
            ("庫存狀態 Inventory", InventoryPage),
            ("產品管理 Products", ProductsPage),
            ("食譜設定 Recipes", RecipesPage),
            ("產品生產 Production", ProductionPage),
            ("POS 匯入 Import POS", POSImportPage),
        ]

        for label, page in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                fg_color="transparent",
                text_color="black",
                anchor="w",
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x", pady=5, padx=10)

    # --------------------------------------------------
    # 切換主視窗頁面
    # --------------------------------------------------
    def show_page(self, page_class):
        # 清除目前頁面
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # 顯示新頁面
        page = page_class(self.main_area)
        page.pack(fill="both", expand=True)


# --------------------------------------------------
# 啟動主程式
# --------------------------------------------------
if __name__ == "__main__":
    app = SweetERPMainApp()
    app.mainloop()
