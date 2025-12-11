#!/bin/zsh

# 移動到腳本所在的位置（自動）
cd "$(dirname "$0")"

echo "🚀 SweetERP Git Push 開始..."

# 加入所有變更
git add .

# 自動產生 commit 訊息包含時間戳
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto update on $timestamp"

# 推送到 main branch
git push origin main

echo "🎉 Push 完成！"
echo "-------------------------"
