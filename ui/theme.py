import customtkinter as ctk

class Color:
    # --- 核心顏色 ---
    PRIMARY = "#3B8ED0"        
    PRIMARY_HOVER = "#36719F"
    
    # --- 背景相關 ---
    MAIN_BG = "#E4E4E4"        
    BACKGROUND = "#E4E4E4"     
    
    WHITE_CARD = "#FFFFFF"     
    SIDEBAR_BG = "#FFFFFF"     
    
    # --- 狀態顏色 ---
    DANGER = "#D03B3B"         
    SUCCESS = "#2CC985"        
    WARNING = "#F1C40F"        
    INFO = "#3B8ED0"           

    # --- 文字顏色 ---
    TEXT_DARK = "#333333"      
    TEXT_LIGHT = "#666666"     
    TEXT_BODY = "#666666"      

    # --- 表格專用 ---
    TABLE_HEADER_BG = "#F0F0F0"
    TABLE_ROW_HEIGHT = 45
    TABLE_ROW_ALT = "#F9F9F9"  # ⚠️ 新增：斑馬紋的淺灰色

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
    BTN_WIDTH = 140
    BTN_HEIGHT = 40
    PAD_X = 20
    PAD_Y = 15