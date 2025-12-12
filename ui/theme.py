import customtkinter as ctk

class Color:
    # --- 核心顏色 ---
    PRIMARY = "#3B8ED0"        # 主色 (藍)
    PRIMARY_HOVER = "#36719F"
    
    # --- 背景 ---
    MAIN_BG = "#E4E4E4"        # 視窗背景
    BACKGROUND = "#E4E4E4"     # 相容變數
    WHITE_CARD = "#FFFFFF"     # 卡片白
    SIDEBAR_BG = "#FFFFFF"     # 側邊欄白
    
    # --- 按鈕專用 ---
    GRAY_BUTTON = "#E0E0E0"        # 次要按鈕底色 (淺灰)
    GRAY_BUTTON_HOVER = "#D6D6D6"  # 次要按鈕懸停
    
    # --- 狀態顏色 ---
    DANGER = "#E74C3C"         # 紅
    SUCCESS = "#16A085"        # 松石綠
    WARNING = "#F39C12"        # 橘黃
    INFO = "#3B8ED0"           # 藍

    # --- 文字 ---
    TEXT_DARK = "#2D3436"      # 深灰
    TEXT_LIGHT = "#636E72"     # 淺灰
    TEXT_BODY = "#2D3436"      

    # --- 表格 ---
    TABLE_HEADER_BG = "#F1F2F6"
    TABLE_ROW_HEIGHT = 40
    TABLE_ROW_ALT = "#FAFAFA"  # 斑馬紋淺灰

class Font:
    TITLE = ("Microsoft JhengHei UI", 26, "bold")
    SUBTITLE = ("Microsoft JhengHei UI", 18, "bold")
    BODY = ("Microsoft JhengHei UI", 16)
    BODY_BOLD = ("Microsoft JhengHei UI", 16, "bold")
    SMALL = ("Microsoft JhengHei UI", 14)
    
    STAT_NUMBER = ("Arial", 30, "bold")
    STAT_LABEL = ("Microsoft JhengHei UI", 12)
    
    # ⚠️ 這裡就是缺少的關鍵變數，補上就不會報錯了
    TABLE_HEADER = ("Microsoft JhengHei UI", 14, "bold")

class Layout:
    BTN_WIDTH = 120
    BTN_HEIGHT = 38
    GRID_PADX = 15 
    GRID_PADY = (5, 15)