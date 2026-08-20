@set FILENAME=Asset_inventory
@cd %CD%
@set LOCATION=%CD%\DIST\%FILENAME%.exe
pyinstaller --onefile %FILENAME%.py
powershell "get-filehash -algorithm sha256 '%LOCATION%' | Format-List"