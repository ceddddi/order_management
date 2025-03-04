@echo off
chcp 65001 > nul
cd %~dp0
call venv\Scripts\activate.bat
echo Запуск Order Management System...
set FLASK_DEBUG=1
set FLASK_ENV=development
start http://127.0.0.1:5000
python -m flask run --debug
pause 