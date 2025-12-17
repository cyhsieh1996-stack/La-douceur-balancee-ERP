import customtkinter as ctk
from PIL import Image
import os
from ui.theme import Color, Font

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=Color.SIDEBAR_BG)
        self.command = command
        self.buttons = {} 
        
        # --- LOGO 區 ---
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(30, 20), padx=20)
        
        # ⚠️ 路徑修正：只往上找一層 (ui -> root)，不是兩層
        current_dir = os.path.dirname(os.path.abspath(__file__)) # .../ui
        project_root = os.path.dirname(current_dir)              # .../SweetERP (根目錄)
        logo_path = os.path.join(project_root, "assets", "logo.png")
        
        # 除錯訊息 (如果成功顯示圖片，這行可以忽略)
        print(f"正在尋找 Logo 路徑: {logo_path}")

        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                # 調整圖片顯示比例 (這裡設為 寬180, 高60，可自行微調)
                # 保持比例縮放
                ratio = pil_image.height / pil_image.width
                new_width = 180
                new_height = int(new_width * ratio)
                
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
                ctk.CTkLabel(self.logo_frame, text="", image=ctk_image).pack()
            except Exception as e:
                print(f"圖片讀取失敗: {e}")
                self.show_text_logo()
        else:
            print("找不到 logo.png，顯示文字版")
            self.show_text_logo()

        # 導覽按鈕容器
        self.nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True, padx=15, pady=10)

        # 建立按鈕
        self.create_nav_button("戰情中心", "dashboard")
        self.create_nav_button("原料管理", "raw_materials")
        self.create_nav_button("產品管理", "products")
        self.create_nav_button("原料入庫", "inbound")
        self.create_nav_button("生產登錄", "production")
        self.create_nav_button("庫存調整", "inventory")
        self.create_nav_button("POS 匯入", "pos_import")

        # 版本號
        version_label = ctk.CTkLabel(self, text="v2.4 Logo Fixed", font=Font.SMALL, text_color=Color.TEXT_LIGHT)
        version_label.pack(side="bottom", pady=20)
        
        # 預設選中
        self.update_active_button("dashboard")

    def show_text_logo(self):
        # 如果沒有圖片，顯示純文字 Logo
        ctk.CTkLabel(self.logo_frame, text="甜點 ERP", font=("Microsoft JhengHei UI", 24, "bold"), text_color=Color.PRIMARY).pack()

    def create_nav_button(self, text, page_name):
        btn = ctk.CTkButton(
            self.nav_container, 
            text=text, 
            font=("Microsoft JhengHei UI", 16, "bold"),
            
            # 樣式：實體膠囊按鈕
            fg_color=Color.SIDEBAR_BTN_DEFAULT,
            text_color=Color.SIDEBAR_TEXT_DEFAULT,
            hover_color=Color.SIDEBAR_BTN_HOVER,
            
            anchor="center", 
            height=48,
            corner_radius=12,
            
            command=lambda: self.handle_click(page_name)
        )
        btn.pack(fill="x", pady=8) 
        self.buttons[page_name] = btn

    def handle_click(self, page_name):
        self.update_active_button(page_name)
        if self.command:
            self.command(page_name)

    def update_active_button(self, page_name):
        for name, btn in self.buttons.items():
            btn.configure(
                fg_color=Color.SIDEBAR_BTN_DEFAULT, 
                text_color=Color.SIDEBAR_TEXT_DEFAULT
            )
        
        if page_name in self.buttons:
            self.buttons[page_name].configure(
                fg_color=Color.SIDEBAR_BTN_ACTIVE, 
                text_color=Color.SIDEBAR_TEXT_ACTIVE
            )