@echo off
title Liquidity Map - Centered Live-Price Game World (XAUUSD)
cd /d "%~dp0"
echo Starting Liquidity Map Game World...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error. Press any key to close...
    pause >nul
)
