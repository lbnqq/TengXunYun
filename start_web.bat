@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python src\web_app.py
pause 