import shutil
import os
import datetime
import glob

# 設定專案根目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sweet_erp.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

def perform_backup():
    """
    執行資料庫備份：
    1. 建立 backups 資料夾
    2. 複製 db 檔案並加上時間戳記
    3. 清理超過 7 天的舊備份
    """
    try:
        # 1. 確保備份資料夾存在
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        # 2. 只有當資料庫存在時才備份
        if os.path.exists(DB_PATH):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"sweet_erp_{timestamp}.db"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            shutil.copy2(DB_PATH, backup_path)
            print(f"✅ 自動備份成功: {backup_filename}")
            
            # 3. 清理舊備份 (保留最近 7 天)
            cleanup_old_backups()
            return True, backup_filename
        else:
            return False, "資料庫檔案不存在"

    except Exception as e:
        print(f"❌ 備份失敗: {e}")
        return False, str(e)

def cleanup_old_backups():
    """刪除超過 7 天的備份檔案"""
    try:
        # 找出所有 .db 備份檔
        files = glob.glob(os.path.join(BACKUP_DIR, "sweet_erp_*.db"))
        files.sort(key=os.path.getmtime) # 按時間排序

        # 如果檔案超過 10 個，或者時間超過 7 天 (這裡簡單實作：只保留最新的 10 個備份)
        # 為了保險起見，我們保留最新的 20 個檔案，刪除更早的
        if len(files) > 20:
            for f in files[:-20]: # 刪除最舊的，只留最後 20 個
                os.remove(f)
                print(f"🗑️ 已清理舊備份: {os.path.basename(f)}")
                
    except Exception as e:
        print(f"清理舊備份時發生錯誤: {e}")