# PowerShell script to create Desktop Shortcut for Liquidity Map
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Liquidity Map.lnk"

$ProjectRoot = "D:\Liquidity Map"
$MainPy = Join-Path -Path $ProjectRoot -ChildPath "main.py"
$IconPath = Join-Path -Path $ProjectRoot -ChildPath "assets\icon.ico"

# Discover pythonw.exe (prefer direct binary over WindowsApps alias)
$KnownBin = "C:\Users\Ruji Tongki\AppData\Local\Python\bin\pythonw.exe"
if (Test-Path $KnownBin) {
    $TargetExe = $KnownBin
} else {
    $PythonCmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($PythonCmd) {
        $TargetExe = $PythonCmd.Source
    } else {
        $TargetExe = "pythonw.exe"
    }
}

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.Arguments = "`"$MainPy`""
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.Description = "Liquidity Map - Centered Live-Price Game World (XAUUSD)"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
Write-Host "Target: $TargetExe `"$MainPy`"" -ForegroundColor Cyan
Write-Host "Icon set to: $IconPath" -ForegroundColor Yellow
