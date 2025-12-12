#!/bin/bash

# 1. 進入此腳本所在的資料夾 (也就是專案根目錄)
cd "$(dirname "$0")"

# 2. 強制使用專案內建的 Python (env/bin/python3) 來執行 main.py
# 這樣可以確保讀取到 env 裡面安裝的套件，也不會報錯找不到 python
./env/bin/python3 main.py

# 3. 暫停，讓視窗不要馬上關閉 (方便看錯誤訊息)
read -p "Press any key to close..."