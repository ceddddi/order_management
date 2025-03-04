Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\Order Management.lnk")
oShellLink.TargetPath = WshShell.CurrentDirectory & "\start_app.bat"
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.IconLocation = "C:\Windows\System32\shell32.dll,21"
oShellLink.Save 