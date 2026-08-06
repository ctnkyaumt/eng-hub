@echo off
setlocal EnableExtensions
title ENG HUB
cd /d "%~dp0"

echo.
echo   ===========================================
echo     ENG HUB  -  baslatiliyor / starting...
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

if defined PYEXE goto run

rem --- 3) Nothing found: offer to install ------------------------------------
echo   Bu bilgisayarda Python bulunamadi.
echo   No Python found on this computer.
echo.
echo   ENG HUB Python 3 ile calisir.
echo     [E] Evet, indir ve kur   (internet gerekir)
echo     [H] Hayir, cikis
echo.
choice /c EH /n /m "Seciminiz (E/H): "
if errorlevel 2 goto bail
call :install
if defined PYEXE goto run
goto bail

:run
echo   Python: %PYEXE%
echo.
"%PYEXE%" "%APP%server\enghub.py"
echo.
echo   ENG HUB kapandi.
timeout /t 3 >nul
exit /b 0

:bail
echo.
echo   Python olmadan ENG HUB baslatilamaz.
echo   Kurulum: https://www.python.org/downloads/
echo.
pause
exit /b 1

rem --------------------------------------------------------------------------
rem  :find <exe>  - first copy on PATH that is Python 3.8 or newer
:find
for /f "delims=" %%I in ('where %1 2^>nul') do (
    if not defined PYEXE call :check "%%I"
)
exit /b 0

:check
"%~1" -c "import sys;raise SystemExit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if not errorlevel 1 set "PYEXE=%~1"
exit /b 0

rem  the py launcher resolves its own interpreter
:findpy
py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%I in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%I"
)
exit /b 0

rem --------------------------------------------------------------------------
:install
set "PYURL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "PYSETUP=%TEMP%\enghub-python-3.11.9.exe"
echo   Indiriliyor / downloading Python 3.11.9 ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { [Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -Uri '%PYURL%' -OutFile '%PYSETUP%' -UseBasicParsing } catch { exit 1 }"
if not exist "%PYSETUP%" (
    echo   Indirme basarisiz. Lutfen elle kurun: https://www.python.org/downloads/
    exit /b 1
)
echo   Kuruluyor / installing ^(PATH'e eklenecek^) ...
"%PYSETUP%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
rem PATH only refreshes for new processes, so look the interpreter up directly
for /f "delims=" %%I in ('dir /b /s "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" 2^>nul') do (
    if not defined PYEXE set "PYEXE=%%I"
)
if not defined PYEXE call :findpy
del "%PYSETUP%" >nul 2>&1
exit /b 0
