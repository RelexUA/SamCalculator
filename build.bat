@echo off
cd /d "%~dp0"
pip install pywebview pyinstaller
pyinstaller --noconsole --onefile --clean --icon favicon.ico --add-data "samsungcalculator.html;." --add-data "favicon.ico;." --name SamsungCalculator app.py
echo.
echo Готово. Программа лежит в папке dist\SamsungCalculator.exe
pause
