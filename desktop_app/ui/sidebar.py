import customtkinter as ctk
from PIL import Image
import os
from ui.theme import Color, Font

class Sidebar(ctk.CTkFrame):
    NAV_SECTIONS = [
        ("工作台", [("dashboard", "今日作業")]),
        ("日常作業", [
            ("inbound", "進貨與入庫"),
            ("production", "生產與批號"),
            ("inventory", "庫存與盤點"),
            ("pos_import", "銷售與 POS"),
        ]),
        ("主檔管理", [
            ("raw_materials", "原料主檔"),
            ("products", "產品主檔"),
        ]),
    ]

    def __init__(self, master, command=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=Color.SIDEBAR_BG)
        self.command = command
        self.buttons = {}
        self.active_page = "dashboard"
        self.switch_in_progress = False
        self.pending_page = None
        
        self.logo_frame = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=18, border_width=1, border_color=Color.BORDER)
        self.logo_frame.pack(fill="x", pady=(26, 18), padx=16)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        logo_path = os.path.join(project_root, "assets", "logo.png")

        print(f"正在尋找 Logo 路徑: {logo_path}")

        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                ratio = pil_image.height / pil_image.width
                new_width = 180
                new_height = int(new_width * ratio)
                
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
                ctk.CTkLabel(self.logo_frame, text="", image=ctk_image).pack(pady=18)
            except Exception as e:
                print(f"圖片讀取失敗: {e}")
                self.show_text_logo()
        else:
            print("找不到 logo.png，顯示文字版")
            self.show_text_logo()

        self.nav_container = ctk.CTkFrame(self, fg_color=Color.WHITE_CARD, corner_radius=18, border_width=1, border_color=Color.BORDER)
        self.nav_container.pack(fill="both", expand=True, padx=16, pady=8)

        for section_title, items in self.NAV_SECTIONS:
            self.create_section_label(section_title)
            for page_name, label in items:
                self.create_nav_button(label, page_name)

        version_label = ctk.CTkLabel(self, text="v2.4", font=Font.SMALL, text_color=Color.TEXT_LIGHT)
        version_label.pack(side="bottom", pady=16)

        self.update_active_button("dashboard")

    def show_text_logo(self):
        ctk.CTkLabel(self.logo_frame, text="甜點 ERP", font=("Avenir Next", 24, "bold"), text_color=Color.PRIMARY).pack(pady=18)

    def create_section_label(self, text):
        ctk.CTkLabel(
            self.nav_container,
            text=text,
            font=Font.SMALL,
            text_color=Color.TEXT_LIGHT,
        ).pack(anchor="w", pady=(16, 6), padx=14)

    def create_nav_button(self, text, page_name):
        btn = ctk.CTkButton(
            self.nav_container, 
            text=text, 
            font=("Microsoft JhengHei UI", 15, "bold"),
            
            fg_color=Color.SIDEBAR_BTN_DEFAULT,
            text_color=Color.SIDEBAR_TEXT_DEFAULT,
            hover_color=Color.SIDEBAR_BTN_HOVER,
            
            anchor="w",
            height=44,
            corner_radius=12,
            
            command=lambda: self.handle_click(page_name)
        )
        btn.pack(fill="x", pady=4, padx=10)
        self.buttons[page_name] = btn

    def handle_click(self, page_name):
        if page_name == self.active_page and not self.switch_in_progress:
            return
        if self.switch_in_progress:
            self.pending_page = page_name
            return
        self.run_switch(page_name)

    def set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in self.buttons.values():
            btn.configure(state=state)

    def run_switch(self, page_name):
        self.switch_in_progress = True
        self.set_buttons_enabled(False)
        success = True
        try:
            if self.command:
                result = self.command(page_name)
                success = True if result is None else bool(result)
            if success:
                self.update_active_button(page_name)
                self.active_page = page_name
        finally:
            self.set_buttons_enabled(True)
            self.switch_in_progress = False

            if self.pending_page and self.pending_page != self.active_page:
                next_page = self.pending_page
                self.pending_page = None
                self.after(0, lambda: self.run_switch(next_page))
            else:
                self.pending_page = None

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

    def sync_active_page(self, page_name):
        self.active_page = page_name
        self.update_active_button(page_name)
