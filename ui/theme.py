# ui/theme.py

class Color:
    # 1. 整體背景色 (參考圖的淺灰色底)
    MAIN_BG = "#E3E3E3"  
    
    # 2. 白色卡片背景 (參考圖的白色區塊)
    WHITE_CARD = "#FFFFFF"
    
    # 3. 側邊選單背景 (稍微深一點的白，或保持白)
    SIDEBAR_BG = "#FFFFFF"
    
    # 4. 主色調 (參考圖的藍色按鈕)
    PRIMARY = "#3B8ED0"  # 這是 customtkinter 預設藍，很接近參考圖
    PRIMARY_HOVER = "#36719F"
    
    # 5. 文字顏色
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#666666"
    
    # 6. 警告/錯誤色
    DANGER = "#D03B3B"
    SUCCESS = "#2CC985"

# 統一的字型設定
class Font:
    TITLE = ("Microsoft JhengHei UI", 24, "bold")
    SUBTITLE = ("Microsoft JhengHei UI", 18, "bold")
    BODY = ("Microsoft JhengHei UI", 14)
    SMALL = ("Microsoft JhengHei UI", 12)