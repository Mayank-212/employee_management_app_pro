@echo off
setlocal enabledelayedexpansion

:: Set working directory to the script's location
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Try to find pythonw.exe in common installation paths
set "PYTHONW_PATH="
for %%P in (
    "C:\Python313\pythonw.exe"
    "%LocalAppData%\Programs\Python\Python313\pythonw.exe"
    "%LocalAppData%\Programs\Python\Python312\pythonw.exe"
    "%LocalAppData%\Programs\Python\Python311\pythonw.exe"
    "%LocalAppData%\Programs\Python\Python310\pythonw.exe"
) do (
    if exist "%%~P" (
        set "PYTHONW_PATH=%%~P"
        goto :FOUND
    )
)

:FOUND
if not defined PYTHONW_PATH (
    echo ❌ Could not find pythonw.exe. Please install Python and add it to PATH.
    pause
    exit /b
)

:: ✅ Run mark_attendance.pyw silently in background
start "" "%PYTHONW_PATH%" "%SCRIPT_DIR%mark_attendance.pyw"

exit /b
