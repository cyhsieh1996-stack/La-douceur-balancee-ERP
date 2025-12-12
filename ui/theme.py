import customtkinter as ctk

class Color:
    PRIMARY = "#3B8ED0"
    PRIMARY_HOVER = "#36719F"
    MAIN_BG = "#E4E4E4"
    BACKGROUND = "#E4E4E4"
    WHITE_CARD = "#FFFFFF"
    SIDEBAR_BG = "#FFFFFF"
    DANGER = "#D03B3B"
    SUCCESS = "#2CC985"
    WARNING = "#F1C40F"
    INFO = "#3B8ED0"
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#666666"
    TEXT_BODY = "#666666"
    TABLE_HEADER_BG = "#F0F0F0"
    TABLE_ROW_HEIGHT = 45

class Font:
    TITLE = ("Microsoft JhengHei UI", 26, "bold")
    SUBTITLE = ("Microsoft JhengHei UI", 18, "bold")
    BODY = ("Microsoft JhengHei UI", 16)
    BODY_BOLD = ("Microsoft JhengHei UI", 16, "bold")
    SMALL = ("Microsoft JhengHei UI", 16)
    STAT_NUMBER = ("Arial", 30, "bold")
    STAT_LABEL = ("Microsoft JhengHei UI", 12)
    TABLE_HEADER = ("Microsoft JhengHei UI", 16, "bold")

class Layout:
    # ⚠️ 新增：統一的按鈕尺寸與間距
    BTN_WIDTH = 140
    BTN_HEIGHT = 40
    PAD_X = 20
    PAD_Y = 15