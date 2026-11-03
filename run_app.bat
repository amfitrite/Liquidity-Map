@echo off
cd /d "%~dp0"
title Liquidity Map
echo Starting Liquidity Map Game World...
if exist "assets\sprites\trails\trail_studio.html" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="file:///%~dp0assets\sprites\trails\trail_studio.html"
) else (
    echo Launching default studio...
    start "" "assets\thumbnail.png"
)
exit
