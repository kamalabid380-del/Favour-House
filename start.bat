@echo off
cd /d "%~dp0"
set "PYEXE=py"
where py >nul 2>nul || set "PYEXE=python"
%PYEXE% manage.py migrate
%PYEXE% manage.py seed_demo
start "Favour House server" cmd /k "%PYEXE% manage.py runserver 8017"
timeout /t 4 >nul
start "" http://127.0.0.1:8017/
