@echo off

:: Get the path of the current directory
set script_dir=%~dp0

:: Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

:: Run the Python script with administrator privileges
python "%script_dir%edgeware.pyw"

pause
