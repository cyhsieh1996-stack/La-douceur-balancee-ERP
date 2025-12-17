import customtkinter as ctk

class Color:
    # --- 主色調 ---
    PRIMARY = "#3B8ED0"        
    PRIMARY_HOVER = "#36719F"
    
    # --- 背景 ---
    MAIN_BG = "#F2F2F2"        # 整體背景稍微灰一點，對比出白色卡片
    WHITE_CARD = "#FFFFFF"     
    
    # --- 側邊欄專用 (恢復經典風格) ---
    SIDEBAR_BG = "#FFFFFF"     # 側邊欄底色
    
    # ⚠️ 這裡改回您喜歡的實體按鈕配色
    SIDEBAR_BTN_DEFAULT = "#F0F0F0"  # 未選中：淺灰底
    SIDEBAR_BTN_HOVER = "#E0E0E0"    # 滑鼠移過去：深一點的灰
    SIDEBAR_BTN_ACTIVE = "#3B5F8F"   # 選中：深藍色 (像截圖那樣)
    
    # 文字顏色
    SIDEBAR_TEXT_DEFAULT = "#2D3436" # 未選中：深灰字
    SIDEBAR_TEXT_ACTIVE = "#FFFFFF"  # 選中：白字
    
    # --- 狀態色 ---
    GRAY_BUTTON = "#E0E0E0"        
    GRAY_BUTTON_HOVER = "#D6D6D6"  
    DANGER = "#E74C3C"         
    SUCCESS = "#10B981"        
    WARNING = "#F59E0B"        
    INFO = "#3B8ED0"           

    # --- 文字 ---
    TEXT_DARK = "#1F2937"      
    TEXT_LIGHT = "#6B7280"     
    TEXT_BODY = "#374151"      

    # --- 表格 ---
    TABLE_HEADER_BG = "#F3F4F6"
    TABLE_ROW_HEIGHT = 38      
    TABLE_ROW_ALT = "#F9FAFB"

class Font:
    TITLE = ("Microsoft JhengHei UI", 22, "bold")
    SUBTITLE = ("Microsoft JhengHei UI", 16, "bold")
    BODY = ("Microsoft JhengHei UI", 15)
    BODY_BOLD = ("Microsoft JhengHei UI", 15, "bold")
    SMALL = ("Microsoft JhengHei UI", 13)
    STAT_NUMBER = ("Arial", 26, "bold")
    STAT_LABEL = ("Microsoft JhengHei UI", 13)
    TABLE_HEADER = ("Microsoft JhengHei UI", 13, "bold")

class Layout:
    BTN_WIDTH = 120
    BTN_HEIGHT = 36
    CARD_PADDING = 20      
    GRID_GAP_X = 20        
    GRID_GAP_Y = 10