@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   ╔══════════════════════════════════╗
echo   ║        余音 - 竹笛学习助手        ║
echo   ╚══════════════════════════════════╝
echo.
echo   正在启动...
echo.
python launcher/main.py
pause
