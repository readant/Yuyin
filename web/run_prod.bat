@echo off
echo 启动余音Web服务器（生产模式）...
echo.

REM 创建日志目录
if not exist "logs" mkdir logs

REM 使用Gunicorn启动
python -m gunicorn -c gunicorn_config.py app:app

pause