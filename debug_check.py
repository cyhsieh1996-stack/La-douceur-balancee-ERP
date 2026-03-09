import sys
import os

# 確保路徑正確
sys.path.append(os.getcwd())

print("----- 開始診斷 -----")
try:
    # 嘗試匯入
    import ui.pages.inventory_page as ip
    
    print(f"✅ Python 找到的檔案路徑是: {ip.__file__}")
    
    print("📋 該檔案裡面的所有東西:")
    attrs = [x for x in dir(ip) if not x.startswith("__")]
    print(attrs)
    
    if 'InventoryPage' in dir(ip):
        print("\n🎉 恭喜！InventoryPage 存在於模組中！")
        print("如果這裡顯示存在，但 main.py 還是報錯，那就是 __pycache__ 的問題。")
    else:
        print("\n❌ 慘！Python 在檔案裡找不到 'InventoryPage'。")
        print("請檢查該檔案是否真的已存檔，或是有縮排錯誤。")
        
except ImportError as e:
    print(f"\n❌ 匯入失敗，原因: {e}")
except Exception as e:
    print(f"\n❌ 發生其他錯誤: {e}")

print("----- 診斷結束 -----")