import tkinter as tk
from tkinter import ttk

# 匯入所有 Page 類別
from ui.pages.dashboard_page import DashboardPage
from ui.pages.raw_materials_page import RawMaterialsPage
from ui.pages.inbound_page import InboundPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.products_page import ProductsPage
from ui.pages.recipes_page import RecipesPage
from ui.pages.material_page import MaterialPage
from ui.pages.reports_page import ReportsPage
from ui.pages.dashboard_page import DashboardPage



class SweetERPMainWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("甘味平橫 SweetERP")
        self.geometry("1280x800")

        # 左側導航列與右側主畫面
        self._create_layout()

        # 建立可切換的頁面對照表
        self.pages = {
            "dashboard": DashboardPage,
            "raw_materials": RawMaterialsPage,
            "inbound": InboundPage,
            "inventory": InventoryPage,
            "products": ProductsPage,
            "recipes": RecipesPage,
            "material": MaterialPage,
        }

        # 啟動預設畫面
        self.show_page("dashboard")

    # --------------------------------------------------------
    # 建立基本 UI 架構：左側選單 ＋ 右側內容區
    # --------------------------------------------------------
    def _create_layout(self):
        # 左側
        self.sidebar = ttk.Frame(self, width=240)
        self.sidebar.pack(side="left", fill="y")

        ttk.Label(self.sidebar, text="SweetERP 功能選單",
                  font=("Arial", 14, "bold")).pack(pady=20)

        # 功能按鈕
        self._add_nav_button("首頁 Dashboard", "dashboard")
        self._add_nav_button("原料主檔管理", "raw_materials")
        self._add_nav_button("新增原料品項", "material")
        self._add_nav_button("原料入庫", "inbound")
        self._add_nav_button("原料盤點/調整", "inventory")
        self._add_nav_button("產品配方管理", "recipes")
        self._add_nav_button("產品管理 / 成本", "products")
        self._add_nav_button("報表中心", "ReportsPage")
        self._add_nav_button("首頁總覽", "DashboardPage")

        # 右側內容顯示區
        self.main_area = ttk.Frame(self)
        self.main_area.pack(side="right", fill="both", expand=True)

    # --------------------------------------------------------
    # 左側按鈕建立器
    # --------------------------------------------------------
    def _add_nav_button(self, text, page_key):
        button = ttk.Button(
            self.sidebar,
            text=text,
            command=lambda: self.show_page(page_key),
            width=25
        )
        button.pack(pady=5)

    # --------------------------------------------------------
    # 切換頁面
    # --------------------------------------------------------
    def show_page(self, key):
        # 清空右側舊畫面
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # 建立並顯示新頁面
        page_class = self.pages.get(key)
        if page_class:
            page = page_class(self.main_area)
            page.pack(fill="both", expand=True)
        else:
            ttk.Label(self.main_area,
                      text=f"⚠ 找不到頁面：{key}",
                      font=("Arial", 16)).pack(pady=50)
