@echo off
REM WisTrade Build Script for Windows
REM 
REM This script builds the Windows executable for WisTrade

echo Building WisTrade executable...

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Build the executable
echo.
echo Building executable...
pyinstaller --clean wistrade.spec

echo.
echo Build complete!
echo Executable location: dist\WisTrade.exe
echo.
pause
