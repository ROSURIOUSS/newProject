@echo off
title SMAK - create admin
cd /d "%~dp0"

if exist ".venv" if not exist ".venv\Scripts\python.exe" rmdir /s /q .venv

call :find_python
if not defined PYCMD goto no_python
if %PYNUM% LSS 310 goto old_python

echo   Python: %PYVER%
echo.

if not exist "manage.py" goto no_project

call :ensure_venv
if errorlevel 1 goto venv_fail

call :ensure_deps
if errorlevel 1 goto pip_fail

echo [3/3] Checking database...
".venv\Scripts\python.exe" manage.py migrate --noinput
if errorlevel 1 goto db_fail

set "EXISTING="
for /f "delims=" %%u in ('".venv\Scripts\python.exe" manage.py shell -v 0 -c "from django.contrib.auth import get_user_model as g;print(' '.join(u.get_username() for u in g().objects.filter(is_superuser=True)))" 2^>nul') do set "EXISTING=%%u"

echo.
if not defined EXISTING goto new_admin

echo   Administrator already exists: %EXISTING%
echo.
echo   [1] Set a new password
echo   [2] Create one more
echo   [0] Do nothing
choice /c 120 /n /m "  Your choice: "
if errorlevel 3 goto finish
if errorlevel 2 goto new_admin

set /p "ADMIN_NAME=  Enter the admin name: "
if not defined ADMIN_NAME goto finish
".venv\Scripts\python.exe" manage.py changepassword %ADMIN_NAME%
goto finish

:new_admin
echo   Enter name, email and password. The password is not shown while typing.
echo.
".venv\Scripts\python.exe" manage.py createsuperuser
if errorlevel 1 goto finish
echo.
echo   Done. Open http://127.0.0.1:8000/admin/ to log in.
goto finish

:finish
echo.
pause
exit /b 0

:ensure_venv
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        echo [1/3] Environment is ready.
        exit /b 0
    )
    echo [1/3] Environment is broken, creating a new one...
    rmdir /s /q .venv
) else (
    echo [1/3] Creating environment...
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
echo [2/3] Dependencies are ready: Django %DJVER%
exit /b 0

:deps_install
echo [2/3] Checking dependencies and installing the missing ones...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -c "import django" >nul 2>&1
if errorlevel 1 exit /b 1
> ".venv\.smak-deps" echo %REQKEY%
for /f "delims=" %%v in ('".venv\Scripts\python.exe" -c "import django;print(django.__version__)"') do set "DJVER=%%v"
echo     Django %DJVER is installed
exit /b 0

:no_project
echo manage.py was not found next to this file.
echo The project folder must contain manage.py and create-admin.bat together.
echo.
pause
exit /b 1

:db_fail
echo.
echo Database could not be prepared. See the message above.
echo.
pause
exit /b 1

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
if exist "%~1" (
    "%~1" -c "import sys" >nul 2>&1
    if not errorlevel 1 set PYCMD2="%~1"
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
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.*") do call :try_py "%%D\python.exe"
if defined PYCMD2 goto :fb_done
for /f "delims=" %%P in ('where python 2^>nul') do call :try_py "%%P"
if defined PYCMD2 goto :fb_done
for /f "delims=" %%P in ('where python3 2^>nul') do call :try_py "%%P"
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
echo Install Python: open https://python.org/downloads
echo tick the box "Add python.exe to PATH" during setup, then run me again.
echo.
echo Or install it from the command line (one line, no clicking):
echo     winget install -e --id Python.Python.3.12
echo After that close this window and start again.
echo.
echo If Python is already installed, start it once from the Start menu
echo and use the option "Add Python to PATH" in its installer.
echo.
pause
exit /b 1
