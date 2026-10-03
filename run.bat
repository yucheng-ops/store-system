@echo off
chcp 65001 >nul
title 門市客戶接洽系統啟動器
cd /d C:\StoreSystem
echo 正在檢查與安裝所需套件...
py -m pip install flask flask-socketio eventlet qrcode pillow >nul 2>&1
echo 啟動系統中...
py app.py
pause