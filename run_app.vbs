Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Liquidity Map"
WshShell.Run "pythonw main.py", 0, False
