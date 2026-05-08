@echo off
chcp 65001 >nul 2>&1
title BusGIS WebGIS - One-Click Installer

echo.
echo ========================================================
echo        BusGIS WebGIS - One-Click Installer
echo ========================================================
echo.
echo  Yeu cau da cai san:
echo    - Python 3.12+
echo    - PostgreSQL 16+ voi PostGIS
echo    - OSGeo4W (GDAL)
echo ========================================================
echo.

:: ── Check Python ──────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [XX] Python chua cai! Tai tai: https://www.python.org/downloads/
    echo      Nho tick "Add python.exe to PATH" khi cai!
    pause
    exit /b 1
)
echo [OK] Python detected
python --version
echo.

:: ── Create venv ───────────────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo [..] Tao virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [XX] Khong tao duoc venv!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment da tao
) else (
    echo [OK] Virtual environment da ton tai
)
echo.

:: ── Activate venv ─────────────────────────────────────────
echo [..] Kich hoat virtual environment...
call venv\Scripts\activate.bat
echo [OK] venv activated
echo.

:: ── Install packages ──────────────────────────────────────
echo [..] Cai dat packages (requirements.txt)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [XX] Loi cai packages! Kiem tra requirements.txt
    pause
    exit /b 1
)
echo [OK] Packages da cai
echo.

:: ── Try GDAL Python binding ───────────────────────────────
echo [..] Thu cai GDAL Python binding...
pip install GDAL --quiet 2>nul
if errorlevel 1 (
    echo [!!] GDAL Python binding khong cai duoc (co the khong can thiet)
) else (
    echo [OK] GDAL Python binding OK
)
echo.

:: ── Run auto setup ────────────────────────────────────────
echo [..] Chay auto setup...
echo.
python auto_setup.py
echo.

:: ── Ask to start server ───────────────────────────────────
echo.
set /p START="Ban co muon chay server ngay bay gio? (y/n): "
if /i "%START%"=="y" (
    echo.
    echo Dang khoi dong server tai http://127.0.0.1:8000 ...
    echo Nhan Ctrl+C de dung server.
    echo.
    python manage.py runserver
)

pause
