@echo off
setlocal enabledelayedexpansion

:: Set working directory to the script's parent folder
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
cd /d "%SCRIPT_DIR%\.."

:: Try to find pythonw.exe in common paths
set PYTHONW_PATH=
for %%P in (
    "C:\Python313\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\pythonw.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\pythonw.exe"
) do (
    if exist %%~P (
        set PYTHONW_PATH=%%~P
        goto :FOUND
    )
)

:FOUND
if not defined PYTHONW_PATH (
    echo ❌ Could not find pythonw.exe. Please install Python and add it to PATH.
    pause
    exit /b
)

:: Run mark_attendance.pyw silently
start "" "!PYTHONW_PATH!" "%SCRIPT_DIR%\..\mark_attendance.pyw"