@echo off
setlocal EnableExtensions
title ENG HUB - Kaynaklari Yenile
cd /d "%~dp0"

echo.
echo   ===========================================
echo     ENG HUB - Kaynaklari Yenile / Refresh
echo   ===========================================
echo.

set "PYEXE="

rem --- 0) Where the program lives: next to this file, or under src\ ---------
set "APP=%~dp0"
if exist "%~dp0src\server\enghub.py" set "APP=%~dp0src\"

rem --- 1) Portable Python on the USB (no install, no admin) ------------------
if exist "%APP%runtime\python-win\python.exe" set "PYEXE=%APP%runtime\python-win\python.exe"

rem --- 2) Python already on this computer ------------------------------------
if not defined PYEXE call :find python.exe
if not defined PYEXE call :find python3.exe
if not defined PYEXE call :findpy

if not defined PYEXE (
    echo   Python bulunamadi.
    pause
    exit /b 1
)

echo   Python: %PYEXE%
echo   Kaynaklar guncelleniyor...
echo.
"%PYEXE%" "%~dp0refresh.py" %*
echo.
pause
exit /b 0

:find
for /f "delims=" %%I in ('where %1 2^>nul') do (
    if not defined PYEXE call :check "%%I"
)
exit /b 0

:check
"%~1" -c "import sys;raise SystemExit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if not errorlevel 1 set "PYEXE=%~1"
exit /b 0

:findpy
py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%I in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%I"
)
exit /b 0
