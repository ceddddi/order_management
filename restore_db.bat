@echo off
chcp 65001 > nul
echo Восстановление базы данных из резервной копии...

:: Проверяем наличие папки backup
if not exist "backup" (
    echo Папка backup не найдена!
    pause
    exit /b 1
)

:: Проверяем наличие файлов резервных копий
dir /b "backup\*.db" > nul 2>&1
if errorlevel 1 (
    echo Резервные копии не найдены!
    pause
    exit /b 1
)

:: Показываем список доступных резервных копий
echo Доступные резервные копии:
echo.
dir /b "backup\*.db"
echo.

:: Запрашиваем имя файла для восстановления
set /p BACKUP_FILE="Введите имя файла для восстановления: "

:: Проверяем существование файла
if not exist "backup\%BACKUP_FILE%" (
    echo Файл не найден!
    pause
    exit /b 1
)

:: Останавливаем Flask если он запущен
taskkill /F /IM python.exe > nul 2>&1

:: Создаем папку instance если её нет
if not exist "instance" mkdir instance

:: Восстанавливаем базу данных
copy "backup\%BACKUP_FILE%" "instance\database.db" > nul

echo.
echo База данных успешно восстановлена!
echo Теперь вы можете запустить приложение через start_app.bat
pause 