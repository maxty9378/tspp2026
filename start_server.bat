@echo off
echo Запуск веб-сервера на http://localhost:8000
echo.
echo Доступные файлы:
echo   - http://localhost:8000/rating_puzzlebot.html
echo   - http://localhost:8000/rating.html
echo.
echo Нажмите Ctrl+C для остановки
echo.
cd /d "%~dp0"
python -m http.server 8000

