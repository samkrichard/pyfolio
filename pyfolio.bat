@echo off
title pyfolio
MODE con:cols=128 lines=40
echo Launching Pyfolio...

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
  echo Activating virtual environment...
  call venv\Scripts\activate.bat
) else (
  echo No virtual environment found. Using system Python.
)

:: Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Please install Python or add it to PATH.
  pause
  exit /b
)

:: Check for required package
pip show pycoingecko >nul 2>nul
if errorlevel 1 (
  echo pycoingecko not found. Installing...
  pip install pycoingecko
)

:: Run the script
echo.
python pyfolio.py

echo.
pause
  