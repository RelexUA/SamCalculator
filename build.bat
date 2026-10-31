@echo off
cd /d "%~dp0"
pip install pywebview pyinstaller
pyinstaller --noconsole --onedir --clean --icon favicon.ico --add-data "samcalculator.html;." --add-data "favicon.ico;." --name SamCalculator app.py
echo.
echo Готово. Программа лежит в папке dist\SamCalculator.exe
pause
