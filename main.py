import customtkinter as ctk
from database.db import init_db
from ui.theme import Color, Font  # 匯入剛剛建立的主題

# 匯入頁面
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
        # 1. 視窗基礎設定
        # ==============================
        self.title("甘味平橫 ERP")
        self.geometry("1400x900")
        
        # 設定為淺色模式，並使用藍色主題
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # ⚠️ 新增：設定 UI 縮放比例 (針對高解析螢幕)
        # 1.0 是預設，1.2 代表放大 20%，您可以試試 1.1 或 1.2
        ctk.set_widget_scaling(1.1)  # 讓按鈕和輸入框變大
        ctk.set_window_scaling(1.1)  # 讓視窗整體內容變大

        # 設定視窗底色 (淺灰)
        self.configure(fg_color=Color.MAIN_BG)

        # ==============================
        # 2. 左側側邊欄 (白色長條)
        # ==============================
        self.sidebar = ctk.CTkFrame(
            self, 
            fg_color=Color.SIDEBAR_BG, 
            width=240, 
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # 側邊欄標題 (Logo區)
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="甘味平橫ERP系統", 
            font=("Arial", 28, "bold"),
            text_color=Color.PRIMARY
        )
        self.logo_label.pack(pady=(40, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar, 
            text="原料產品進銷管理", 
            font=Font.SMALL,
            text_color=Color.TEXT_LIGHT
        )
        self.subtitle_label.pack(pady=(0, 30))

        # ==============================
        # 3. 建立側邊欄按鈕
        # ==============================
        self.current_btn = None # 紀錄目前被選中的按鈕
        self.create_sidebar_buttons()

        # ==============================
        # 4. 右側主內容區 (放置頁面的地方)
        # ==============================
        # 這裡不放任何顏色，讓它透出底部的淺灰，這樣頁面的白色卡片才會明顯
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # 預設顯示儀表板
        self.show_page(DashboardPage, "儀表板 Dashboard")


    def create_sidebar_buttons(self):
        # 按鈕清單
        self.nav_buttons = {} # 用字典存起來，方便切換樣式
        
        menu_items = [
            ("主儀表板", DashboardPage),
            ("原料管理", RawMaterialsPage),
            ("原料入庫", InboundPage),
            ("庫存調整", InventoryPage),
            ("產品管理", ProductsPage),
            ("食譜設定", RecipesPage),
            ("生產登錄", ProductionPage),
            ("POS 匯入", POSImportPage),
        ]

        for text, page in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=Font.BODY,
                fg_color="transparent",        # 預設透明背景
                text_color=Color.TEXT_DARK,    # 預設深灰字
                hover_color="#F0F0F0",         # 滑鼠移過去變淺灰
                anchor="w",                    # 文字靠左
                height=45,
                corner_radius=8,
                command=lambda p=page, t=text: self.show_page(p, t)
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[text] = btn


    def show_page(self, page_class, title_text):
        # 1. 切換按鈕樣式 (模擬 Active State)
        for btn_text, btn in self.nav_buttons.items():
            if btn_text == title_text:
                # 選中的按鈕：變成藍色底、白字
                btn.configure(fg_color=Color.PRIMARY, text_color="white", hover_color=Color.PRIMARY_HOVER)
            else:
                # 未選中：透明底、黑字
                btn.configure(fg_color="transparent", text_color=Color.TEXT_DARK, hover_color="#F0F0F0")

        # 2. 清除舊頁面
        for widget in self.main_area.winfo_children():
            widget.destroy()

        # 3. 載入新頁面
        try:
            # 我們傳入 main_area，頁面自己會變成一張卡片
            page = page_class(self.main_area)
            page.pack(fill="both", expand=True)
        except Exception as e:
            err = ctk.CTkLabel(self.main_area, text=f"頁面載入失敗: {e}", text_color="red")
            err.pack()

if __name__ == "__main__":
    print("正在檢查資料庫...")
    init_db()
    app = SweetERPMainApp()
    app.mainloop()