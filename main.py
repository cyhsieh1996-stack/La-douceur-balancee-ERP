import customtkinter as ctk
import os
from PIL import Image

from database.db import init_db
from ui.theme import Color, Font

# 匯入頁面 (移除 RecipesPage)
from ui.pages.dashboard_page import DashboardPage
from ui.pages.raw_materials_page import RawMaterialsPage
from ui.pages.inbound_page import InboundPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.products_page import ProductsPage
# from ui.pages.recipes_page import RecipesPage  <-- 已移除
from ui.pages.production_page import ProductionPage
from ui.pages.pos_import_page import POSImportPage

class SweetERPMainApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1. 視窗設定
        self.title("SweetERP ｜ 甘味平橫 ERP")
        self.geometry("1400x900")
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.1)
        ctk.set_window_scaling(1.1)

        self.configure(fg_color=Color.MAIN_BG)

        # 2. 側邊欄
        self.sidebar = ctk.CTkFrame(
            self, 
            fg_color=Color.SIDEBAR_BG, 
            width=240, 
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # --- Logo 區域 ---
        image_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        
        try:
            pil_image = Image.open(image_path)
            logo_image = ctk.CTkImage(light_image=pil_image, 
                                      dark_image=pil_image, 
                                      size=(140, 140))
            
            self.logo_label = ctk.CTkLabel(self.sidebar, text="", image=logo_image)
            self.logo_label.pack(pady=(30, 10))

        except Exception as e:
            print(f"Logo 載入失敗: {e}")
            self.logo_label = ctk.CTkLabel(
                self.sidebar, 
                text="SweetERP", 
                font=("Arial", 28, "bold"),
                text_color=Color.PRIMARY
            )
            self.logo_label.pack(pady=(40, 10))
             
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar, 
            text="ERP管理系統", 
            font=Font.SMALL,
            text_color=Color.TEXT_LIGHT
        )
        self.subtitle_label.pack(pady=(0, 20))

        # 3. 按鈕與內容區
        self.nav_buttons = {} 
        self.create_sidebar_buttons()

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.show_page(DashboardPage, "主儀表板")


    def create_sidebar_buttons(self):
        # ⚠️ 修改：移除了「食譜設定」
        menu_items = [
            ("主儀表板", DashboardPage),
            ("原料管理", RawMaterialsPage),
            ("原料入庫", InboundPage),
            ("庫存調整", InventoryPage),
            ("產品管理", ProductsPage),
            # ("食譜設定", RecipesPage), <-- 已移除
            ("產品生產", ProductionPage),
            ("POS 匯入", POSImportPage),
        ]

        btn_font = ctk.CTkFont(family="Microsoft JhengHei UI", size=13, weight="bold")

        for text, page in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=btn_font,
                fg_color="#F0F0F0",
                text_color=Color.TEXT_DARK,
                hover_color="#E0E0E0",
                anchor="center",
                height=40,
                corner_radius=10,
                command=lambda p=page, t=text: self.show_page(p, t)
            )
            btn.pack(fill="x", padx=25, pady=5)
            self.nav_buttons[text] = btn


    def show_page(self, page_class, title_text):
        for btn_text, btn in self.nav_buttons.items():
            if btn_text == title_text:
                btn.configure(fg_color=Color.PRIMARY, text_color="white", hover_color=Color.PRIMARY_HOVER)
            else:
                btn.configure(fg_color="#F0F0F0", text_color=Color.TEXT_DARK, hover_color="#E0E0E0")

        for widget in self.main_area.winfo_children():
            widget.destroy()

        try:
            page = page_class(self.main_area)
            page.pack(fill="both", expand=True)
        except Exception as e:
            err_frame = ctk.CTkFrame(self.main_area, fg_color="white")
            err_frame.pack(expand=True, fill="both")
            ctk.CTkLabel(err_frame, text=f"頁面載入失敗: {e}", text_color="red", font=("Arial", 16)).pack(expand=True)
            print(f"Error loading {title_text}: {e}")

if __name__ == "__main__":
    init_db()
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "assets")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "assets"))
        
    app = SweetERPMainApp()
    app.mainloop()