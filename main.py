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


class SweetERPMainApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ==============================
        # 主視窗設定
        # ==============================
        self.title("SweetERP - 甘味平橫 ERP")
        self.geometry("1350x850")
        self.minsize(1200, 700)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 主背景
        self.configure(fg_color="#F5F5F5")

        # ==============================
        # 上方橫幅區
        # ==============================
        top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        top_bar.pack(fill="x")

        title_label = ctk.CTkLabel(
            top_bar,
            text="SweetERP ｜ 甘味平橫 ERP 系統",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#333333"
        )
        title_label.pack(side="left", padx=25, pady=18)

        underline = ctk.CTkFrame(self, fg_color="#D6D6D6", height=1)
        underline.pack(fill="x")

        # ==============================
        # 左側側邊欄
        # ==============================
        sidebar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, width=220)
        sidebar.pack(side="left", fill="y")

        self.sidebar = sidebar

        # ==============================
        # 主內容區（右側）
        # ==============================
        self.main_area = ctk.CTkFrame(self, fg_color="#F5F5F5")
        self.main_area.pack(side="right", fill="both", expand=True)

        # 建立側邊欄按鈕
        self.create_sidebar_buttons()

        # 預設顯示儀表板
        self.show_page(DashboardPage)

    # =======================================
    # 建立側邊欄按鈕
    # =======================================
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

        for text, page in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#E8C7A3",   # 淡杏色 hover
                text_color="#333333",
                anchor="w",
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x", padx=15, pady=6)


    # =======================================
    # 切換主內容頁
    # =======================================
    def show_page(self, page_class):

        # 清除原本內容
        for widget in self.main_area.winfo_children():
            widget.destroy()

        page = page_class(self.main_area)
        page.pack(fill="both", expand=True)


# =======================================
# 啟動程式
# =======================================
if __name__ == "__main__":
    app = SweetERPMainApp()
    app.mainloop()
