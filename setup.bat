@echo off
chcp 65001 > nul
echo Установка Order Management System
echo ==============================
echo.

:: Проверка наличия Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Python не установлен!
    echo Пожалуйста, установите Python с сайта https://www.python.org/downloads/
    echo И не забудьте отметить галочку "Add Python to PATH" при установке
    pause
    exit /b 1
)

:: Создание виртуального окружения
echo Создание виртуального окружения...
python -m venv venv
if errorlevel 1 (
    echo Ошибка при создании виртуального окружения!
    pause
    exit /b 1
)

:: Активация виртуального окружения и установка зависимостей
echo Установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка при установке зависимостей!
    pause
    exit /b 1
)

:: Инициализация базы данных
echo Инициализация базы данных...
python database.py
if errorlevel 1 (
    echo Ошибка при инициализации базы данных!
    pause
    exit /b 1
)

echo.
echo ==============================
echo Установка успешно завершена!
echo.
echo Для запуска приложения используйте start_app.bat
echo.
pause 