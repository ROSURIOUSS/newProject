@echo off
title СМАК - создание администратора
cd /d "%~dp0"

call :find_python
if not defined PYCMD goto no_python
if %PYNUM% LSS 310 goto old_python

echo   Python: %PYVER%
echo.

if not exist "manage.py" goto no_project

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Готовлю окружение...
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

echo [2/3] Проверяю базу...
".venv\Scripts\python.exe" manage.py migrate --noinput
if errorlevel 1 goto db_fail

set "EXISTING="
for /f "delims=" %%u in ('".venv\Scripts\python.exe" manage.py shell -v 0 -c "from django.contrib.auth import get_user_model as g;print(' '.join(u.get_username() for u in g().objects.filter(is_superuser=True)))" 2^>nul') do set "EXISTING=%%u"

echo [3/3] Администратор.
echo.

if not defined EXISTING goto new_admin

echo   Уже есть администратор: %EXISTING%
echo.
echo   [1] Задать новый пароль
echo   [2] Создать еще одного
echo   [0] Ничего не делать
choice /c 120 /n /m "  Мой выбор: "
if errorlevel 3 goto finish
if errorlevel 2 goto new_admin

set /p "ADMIN_NAME=  Введите имя администратора: "
if not defined ADMIN_NAME goto finish
".venv\Scripts\python.exe" manage.py changepassword %ADMIN_NAME%
goto finish

:new_admin
echo   Придумайте имя, почту и пароль. Пароль при вводе не отображается.
echo.
".venv\Scripts\python.exe" manage.py createsuperuser
if errorlevel 1 goto finish
echo.
echo   Готово. Вход: http://127.0.0.1:8000/admin/
goto finish

:finish
echo.
pause
exit /b 0

:no_project
echo Рядом с этим файлом должен лежать manage.py.
echo Распакуйте проект так, чтобы create-admin.bat лежал в папке с manage.py.
echo.
pause
exit /b 1

:db_fail
echo.
echo База не подготовилась. Ниже - что именно не так.
echo.
pause
exit /b 1
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
