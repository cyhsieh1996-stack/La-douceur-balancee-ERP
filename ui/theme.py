# ui/theme.py

class Color:
    # 1. 背景色
    MAIN_BG = "#E3E3E3"  
    WHITE_CARD = "#FFFFFF"
    SIDEBAR_BG = "#FFFFFF"
    
    # 2. 主色調
    PRIMARY = "#3B8ED0"
    PRIMARY_HOVER = "#36719F"
    
    # 3. 文字顏色
    TEXT_DARK = "#333333"
    TEXT_LIGHT = "#666666"
    
    # 4. 狀態色
    DANGER = "#D03B3B"
    SUCCESS = "#2CC985"

# 修改：加大字體設定
class Font:
    # 標題從 24 -> 28
    TITLE = ("Microsoft JhengHei UI", 28, "bold")
    
    # 副標題從 18 -> 20
    SUBTITLE = ("Microsoft JhengHei UI", 20, "bold")
    
    # 內文從 14 -> 16 (這會影響輸入框和標籤)
    BODY = ("Microsoft JhengHei UI", 16)
    
    # 小字從 12 -> 16 (表格內容通常用這個)
    SMALL = ("Microsoft JhengHei UI", 16)
    
    # 表格表頭特別設定大一點
    TABLE_HEADER = ("Microsoft JhengHei UI", 14, "bold")