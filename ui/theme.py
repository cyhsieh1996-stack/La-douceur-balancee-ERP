import customtkinter as ctk

class Color:
    PRIMARY = "#3B8ED0"        
    PRIMARY_HOVER = "#36719F"
    MAIN_BG = "#E4E4E4"        
    BACKGROUND = "#E4E4E4"     
    WHITE_CARD = "#FFFFFF"     
    SIDEBAR_BG = "#FFFFFF"     
    GRAY_BUTTON = "#AAAAAA"        
    GRAY_BUTTON_HOVER = "#999999"  
    DANGER = "#E74C3C"         
    SUCCESS = "#16A085"        
    WARNING = "#F39C12"        
    INFO = "#3B8ED0"           
    TEXT_DARK = "#2D3436"      
    TEXT_LIGHT = "#636E72"     
    TEXT_BODY = "#2D3436"      
    TABLE_HEADER_BG = "#F1F2F6"
    TABLE_ROW_HEIGHT = 45 # 稍微加高一點，比較不擁擠
    TABLE_ROW_ALT = "#FAFAFA"

class Font:
    TITLE = ("Microsoft JhengHei UI", 26, "bold")
    SUBTITLE = ("Microsoft JhengHei UI", 18, "bold")
    BODY = ("Microsoft JhengHei UI", 15) # 微調字體大小
    BODY_BOLD = ("Microsoft JhengHei UI", 15, "bold")
    SMALL = ("Microsoft JhengHei UI", 13)
    STAT_NUMBER = ("Arial", 30, "bold")
    STAT_LABEL = ("Microsoft JhengHei UI", 12)
    TABLE_HEADER = ("Microsoft JhengHei UI", 14, "bold")

class Layout:
    BTN_WIDTH = 110
    BTN_HEIGHT = 36
    # ⚠️ 關鍵：定義統一的內距
    CARD_PADDING = 20      # 卡片內邊距
    GRID_GAP_X = 20        # 欄位左右間距
    GRID_GAP_Y = 15        # 欄位上下間距 (含Label)