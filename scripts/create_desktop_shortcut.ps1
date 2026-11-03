# PowerShell script to create Desktop Shortcut for Liquidity Map
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Liquidity Map.lnk"

$ProjectRoot = "D:\Liquidity Map"
$TargetBat = Join-Path -Path $ProjectRoot -ChildPath "run_app.bat"
$IconPath = Join-Path -Path $ProjectRoot -ChildPath "assets\icon.ico"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetBat
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.Description = "Liquidity Map - Centered Live-Price Game World (XAUUSD)"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
Write-Host "Icon set to: $IconPath" -ForegroundColor Cyan
