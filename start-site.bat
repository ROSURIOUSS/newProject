@echo off
title SMAK - local site
cd /d "%~dp0"

if exist ".venv" if not exist ".venv\Scripts\python.exe" rmdir /s /q .venv

call :find_python
if not defined PYCMD goto no_python
if %PYNUM% LSS 310 goto old_python

echo   Python: %PYVER%
echo.

call :ensure_venv
if errorlevel 1 goto venv_fail

call :ensure_deps
if errorlevel 1 goto pip_fail

if not exist "db.sqlite3" (
    echo [3/4] Preparing database and menu...
    ".venv\Scripts\python.exe" manage.py migrate
    ".venv\Scripts\python.exe" manage.py load_menu
) else (
    echo [3/4] Database and menu are ready.
)

echo [4/4] Starting server...
echo.
echo   Site:     http://127.0.0.1:8000/
echo   Admin:    http://127.0.0.1:8000/admin/
echo   To log in to admin run create-admin.bat first
echo   Stop:     Ctrl+C or close this window
echo.
start "" /b cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000/"
".venv\Scripts\python.exe" manage.py runserver
echo.
echo Server stopped.
pause
exit /b 0

:ensure_venv
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        echo [1/4] Environment is ready.
        exit /b 0
    )
    echo [1/4] Environment is broken, creating a new one...
    rmdir /s /q .venv
) else (
    echo [1/4] Creating environment...
)
call :find_base
if not defined BASECMD (
    echo Python for creating the environment was not found.
    exit /b 1
)
%BASECMD% -m venv .venv
if not exist ".venv\Scripts\python.exe" exit /b 1
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip >nul 2>&1
exit /b 0

:ensure_deps
set "REQKEY=none"
if exist "requirements.txt" for %%A in ("requirements.txt") do set "REQKEY=%%~zA_%%~tA"
set "MARKED="
if exist ".venv\.smak-deps" set /p MARKED=<".venv\.smak-deps"

".venv\Scripts\python.exe" -c "import django,sys;v=tuple(int(x) for x in django.__version__.split('.')[:2]);sys.exit(0 if (5,0)<=v<(7,0) else 1)" >nul 2>&1
if errorlevel 1 goto deps_install
if /i not "%MARKED%"=="%REQKEY%" goto deps_install
for /f "delims=" %%v in ('".venv\Scripts\python.exe" -c "import django;print(django.__version__)"') do set "DJVER=%%v"
echo [2/4] Dependencies are ready: Django %DJVER%
exit /b 0

:deps_install
echo [2/4] Checking dependencies and installing the missing ones...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -c "import django" >nul 2>&1
if errorlevel 1 exit /b 1
> ".venv\.smak-deps" echo %REQKEY%
for /f "delims=" %%v in ('".venv\Scripts\python.exe" -c "import django;print(django.__version__)"') do set "DJVER=%%v"
echo     Django %DJVER is installed
exit /b 0

:venv_fail
echo.
echo Could not create the .venv environment.
echo Python is installed but cannot write to this folder.
echo Try to copy the project to another folder, for example C:\projects
echo.
pause
exit /b 1

:pip_fail
echo.
echo Packages were not installed. Check the internet connection
echo and run this file again.
echo.
pause
exit /b 1

:try_py
if defined PYCMD2 exit /b 0
if exist %1 (
    %1 -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PYCMD2=%1"
)
exit /b 0

:try_reg
if defined PYCMD2 exit /b 0
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Python\PythonCore" /s /v ExecutablePath 2^>nul ^| findstr /i "ExecutablePath"') do call :try_py "%%B"
if defined PYCMD2 exit /b 0
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Python\PythonCore" /s /v ExecutablePath 2^>nul ^| findstr /i "ExecutablePath"') do call :try_py "%%B"
exit /b 0

:find_base
set "PYCMD2="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD2=py -3"
    goto :fb_done
)
python -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD2=python"
    goto :fb_done
)
python3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD2=python3"
    goto :fb_done
)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do call :try_py "%%D\python.exe"
if defined PYCMD2 goto :fb_done
for /d %%D in ("%ProgramFiles%\Python3*") do call :try_py "%%D\python.exe"
if defined PYCMD2 goto :fb_done
for /d %%D in ("%ProgramFiles(x86)%\Python3*") do call :try_py "%%D\python.exe"
if defined PYCMD2 goto :fb_done
for /d %%D in ("C:\Python3*") do call :try_py "%%D\python.exe"
if defined PYCMD2 goto :fb_done
call :try_reg
:fb_done
set "BASECMD=%PYCMD2%"
exit /b 0

:find_python
set "PYCMD="
set "PYVER="
set "PYNUM=999"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PYCMD=".venv\Scripts\python.exe""
        goto :fp_ok
    )
)
call :find_base
if defined BASECMD set "PYCMD=%BASECMD%"
if not defined PYCMD exit /b 0

:fp_ok
for /f "delims=" %%v in ('%PYCMD% -c "import sys;print(sys.version.split()[0])"') do set "PYVER=%%v"
for /f "delims=" %%v in ('%PYCMD% -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])"') do set "PYNUM=%%v"
exit /b 0

:old_python
echo.
echo Found Python %PYVER%, but version 3.10 or newer is required.
echo Install a fresh one from https://python.org/downloads
echo.
pause
exit /b 1

:no_python
echo.
echo Python was not found on this computer.
echo.
echo What the system sees:
where py 2>nul
where python 2>nul
where python3 2>nul
echo.
echo A path with WindowsApps inside means a Microsoft Store stub.
echo That stub does not work, it is skipped on purpose.
echo.
echo Install Python from https://python.org/downloads
echo and tick the box "Add python.exe to PATH" during setup.
echo If Python is already installed, run it once from the Start menu,
echo then use the option "Add Python to PATH" in its installer.
echo.
pause
exit /b 1
