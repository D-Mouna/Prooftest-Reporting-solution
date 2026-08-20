cd C:\Projekte\Python\Plug-In\O_Scope
pyinstaller --onefile O_Scope.py
powershell "get-filehash -algorithm sha256 'C:\Projekte\Python\Plug-In\O_Scope\dist\O_Scope.exe' | Format-List"