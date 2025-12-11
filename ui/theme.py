import customtkinter as ctk

class SweetTheme:

    @staticmethod
    def apply(root):
        root.configure(fg_color="#F7F4EF")   # 奶油白主背景色
        ctk.set_default_color_theme("blue")

        # 色票
        SweetTheme.accent = "#A37A52"       # 焦糖棕
        SweetTheme.accent_light = "#D6C2A8"
        SweetTheme.text_dark = "#4A4A48"
        SweetTheme.bg_light = "#F7F4EF"
        SweetTheme.bg_panel = "#EFECE7"
