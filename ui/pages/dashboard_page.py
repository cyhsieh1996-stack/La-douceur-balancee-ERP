import customtkinter as ctk
from logic.dashboard_logic import get_total_material_stock
from ui.theme import Color, Font  # 匯入主題

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master):
        # 注意：這裡 fg_color設為透明，讓它透出主視窗的灰底
        super().__init__(master, fg_color="transparent")

        # ==========================================
        # 1. 標題區 (直接顯示在灰底上)
        # ==========================================
        title = ctk.CTkLabel(
            self, 
            text="儀表板 Dashboard", 
            font=Font.TITLE, 
            text_color=Color.TEXT_DARK
        )
        title.pack(anchor="w", pady=(0, 20))

        # ==========================================
        # 2. 卡片區 (這就是參考圖那個白色的框框)
        # ==========================================
        # 建立一個大卡片容器
        card_container = ctk.CTkFrame(
            self, 
            fg_color=Color.WHITE_CARD,  # 白色背景
            corner_radius=15            # 圓角
        )
        card_container.pack(fill="both", expand=True)

        # 在卡片裡面放內容
        self.create_content(card_container)

    def create_content(self, parent):
        # 模擬一個簡單的數據顯示
        try:
            total_material = get_total_material_stock()
        except:
            total_material = 0

        # 資訊小方塊
        info_box = ctk.CTkFrame(parent, fg_color="#F0F5F9", corner_radius=10)
        info_box.pack(padx=30, pady=30, fill="x", anchor="n")

        label = ctk.CTkLabel(
            info_box, 
            text="原料總庫存量", 
            font=Font.SUBTITLE, 
            text_color=Color.TEXT_LIGHT
        )
        label.pack(padx=20, pady=(20, 5), anchor="w")

        value = ctk.CTkLabel(
            info_box, 
            text=f"{total_material:,.1f}", 
            font=("Arial", 48, "bold"), 
            text_color=Color.PRIMARY
        )
        value.pack(padx=20, pady=(0, 20), anchor="w")

        # 這裡可以繼續加更多圖表或清單...