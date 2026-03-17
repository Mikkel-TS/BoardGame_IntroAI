@echo off
setlocal

set "ROOT=%~dp0"
set "SCRIPT=%ROOT%boop\main.py"

if exist "%LocalAppData%\Programs\Python\Python313\pythonw.exe" (
    start "" "%LocalAppData%\Programs\Python\Python313\pythonw.exe" "%SCRIPT%"
    exit /b 0
)

if exist "%LocalAppData%\Programs\Python\Python312\pythonw.exe" (
    start "" "%LocalAppData%\Programs\Python\Python312\pythonw.exe" "%SCRIPT%"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%SCRIPT%"
    exit /b 0
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%SCRIPT%"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    start "" py "%SCRIPT%"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" python "%SCRIPT%"
    exit /b 0
)

echo Could not find Python on this computer.
echo Please install Python 3 and then run this file again.
pause
