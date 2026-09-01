@echo off
REM Launch the In-Takt Django dev server (Windows native — no WSL)
REM This file lives in the project root, so the script resolves itself
REM regardless of where it is launched from.
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXEC=%PROJECT_DIR%venv\Scripts\python.exe"

cd /d "%PROJECT_DIR%"

if not exist "%PYTHON_EXEC%" (
    echo [ERROR] venv\Scripts\python.exe not found under "%PROJECT_DIR%".
    echo [ERROR] First create the virtual environment:  python -m venv venv
    echo [ERROR] Then install dependencies:             venv\Scripts\pip install -r requirements.txt
    goto :fail
)

echo Starting Django dev server on http://localhost:8080 ...
"%PYTHON_EXEC%" manage.py runserver 0.0.0.0:8080
goto :eof

:fail
set "EXITCODE=1"
endlocal & exit /b %EXITCODE%