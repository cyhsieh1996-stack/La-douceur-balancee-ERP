import customtkinter as ctk

# ----------------------------
#  分頁匯入
# ----------------------------
from ui.pages.dashboard_page import DashboardPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.inbound_page import InboundPage
from ui.pages.products_page import ProductsPage
from ui.pages.recipes_page import RecipesPage
from ui.pages.pos_import_page import POSImportPage
from ui.pages.production_page import ProductionPage  # ★★★ 生產管理頁


# ----------------------------
#  全域 UI 設定
# ----------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SweetERPMainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("甘味平橫 SweetERP")
        self.geometry("1250x800")
        self.configure(fg_color="#F7F4EF")

        # -------------------------------------
        # 左側 Sidebar
        # -------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#FFFFFF")
        self.sidebar.pack(side="left", fill="y")

        # Logo & Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="🍰 SweetERP",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4A4A48",
        )
        title_label.pack(pady=25)

        # 按鈕共同設定
        btn_cfg = {
            "width": 190,
            "height": 45,
            "corner_radius": 8,
            "font": ctk.CTkFont(size=15),
        }

        # Sidebar Buttons
        self.create_sidebar_button("Dashboard 儀表板", "dashboard", btn_cfg)
        self.create_sidebar_button("庫存總覽", "inventory", btn_cfg)
        self.create_sidebar_button("原料入庫", "inbound", btn_cfg)
        self.create_sidebar_button("商品管理", "products", btn_cfg)
        self.create_sidebar_button("食譜管理", "recipes", btn_cfg)
        self.create_sidebar_button("生產管理", "production", btn_cfg)     # ★★★ 新增
        self.create_sidebar_button("POS 資料匯入", "pos_import", btn_cfg)

        # -------------------------------------
        # 主內容 Frame
        # -------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#F7F4EF")
        self.main_frame.pack(side="right", expand=True, fill="both")

        # 頁面快取
        self.pages = {}
        self.current_page = None

        # 預設開啟 Dashboard
        self.show_page("dashboard")

    # -------------------------------------
    # 建立側邊按鈕（共用方法）
    # -------------------------------------
    def create_sidebar_button(self, text, page_name, cfg):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=lambda: self.show_page(page_name),
            **cfg
        )
        btn.pack(pady=5)

    # -------------------------------------
    # 分頁切換邏輯
    # -------------------------------------
    def show_page(self, name: str):

        # 隱藏目前頁面
        if self.current_page is not None:
            self.current_page.pack_forget()

        # 建立頁面（若無 cache）
        if name not in self.pages:

            if name == "dashboard":
                frame = DashboardPage(self.main_frame)

            elif name == "inventory":
                frame = InventoryPage(self.main_frame)

            elif name == "inbound":
                frame = InboundPage(self.main_frame)

            elif name == "products":
                frame = ProductsPage(self.main_frame)
                if hasattr(frame, "refresh"):
                    frame.refresh()

            elif name == "recipes":
                frame = RecipesPage(self.main_frame)
                if hasattr(frame, "refresh"):
                    frame.refresh()

            elif name == "production":   # ★★★ 生產管理
                frame = ProductionPage(self.main_frame)

            elif name == "pos_import":
                frame = POSImportPage(self.main_frame)

            else:
                return

            self.pages[name] = frame

        # 顯示新頁面
        self.current_page = self.pages[name]
        self.current_page.pack(expand=True, fill="both")


# -------------------------------------
# Program Entry Point
# -------------------------------------
if __name__ == "__main__":
    app = SweetERPMainWindow()
    app.mainloop()
