@echo off
title СМАК - локальный сайт
cd /d "%~dp0"

call :find_python
if not defined PYCMD goto no_python
if %PYNUM% LSS 310 goto old_python

echo   Python: %PYVER%   [%PYSHOW%]
echo.

if exist ".venv" if not exist ".venv\Scripts\python.exe" rmdir /s /q .venv

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Первый запуск: создаю окружение и ставлю зависимости...
    %PYCMD% -m venv .venv
    if not exist ".venv\Scripts\python.exe" goto venv_fail
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if exist "requirements.txt" (
        ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    ) else (
        ".venv\Scripts\python.exe" -m pip install "Django>=5.0,<7.0"
    )
    if errorlevel 1 goto pip_fail
) else (
    echo [1/3] Окружение на месте.
)

if not exist "db.sqlite3" (
    echo [2/3] Готовлю базу и меню...
    ".venv\Scripts\python.exe" manage.py migrate
    ".venv\Scripts\python.exe" manage.py load_menu
) else (
    echo [2/3] База и меню на месте.
)

echo [3/3] Запускаю сервер...
echo.
echo   Сайт:      http://127.0.0.1:8000/
echo   Админка:   http://127.0.0.1:8000/admin/
echo   Вход в админку: сначала запустите create-admin.bat
echo   Остановка: Ctrl+C или закрыть это окно
echo.
start "" /b cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000/"
".venv\Scripts\python.exe" manage.py runserver
echo.
echo Сервер остановлен.
pause
exit /b 0

:venv_fail
echo.
echo Не удалось создать окружение .venv.
echo Проверьте, что Python установлен с python.org и доступен на запись.
echo.
pause
exit /b 1

:pip_fail
echo.
echo Зависимости не установились. Проверьте интернет и повторите запуск.
echo.
pause
exit /b 1

:find_python
set "PYCMD="
set "PYSHOW="
set "PYVER="
set "PYNUM=999"

py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD=py -3"
    set "PYSHOW=py -3"
    goto :fp_ok
)

python -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD=python"
    set "PYSHOW=python"
    goto :fp_ok
)

python3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD=python3"
    set "PYSHOW=python3"
    goto :fp_ok
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PYCMD="%%D\python.exe""
            set "PYSHOW=%%D\python.exe"
            goto :fp_ok
        )
    )
)
for /d %%D in ("C:\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PYCMD="%%D\python.exe""
            set "PYSHOW=%%D\python.exe"
            goto :fp_ok
        )
    )
)
exit /b 0

:fp_ok
for /f "delims=" %%v in ('%PYCMD% -c "import sys;print(sys.version.split()[0])"') do set "PYVER=%%v"
for /f "delims=" %%v in ('%PYCMD% -c "import sys;print(sys.version_info[0]*100+sys.version_info[1])"') do set "PYNUM=%%v"
exit /b 0

:old_python
echo.
echo Найден Python %PYVER%, но нужен 3.10 или новее.
echo Поставьте свежий с https://python.org/downloads
echo.
pause
exit /b 1

:no_python
echo.
echo Python не найден или не запускается.
echo.
echo Что видит система:
where py 2>nul
where python 2>nul
where python3 2>nul
echo.
echo Если выше есть путь ...\WindowsApps\python.exe - это заглушка
echo Microsoft Store, она не работает. Батник ее пропускает и ищет дальше.
echo.
echo Поставьте Python с https://python.org/downloads
echo и при установке отметьте галочку "Add python.exe to PATH".
echo.
pause
exit /b 1
