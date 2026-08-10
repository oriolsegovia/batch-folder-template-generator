@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py"
) else (
    set "PY=python"
)

%PY% -m pip install --user --upgrade pyinstaller customtkinter
if errorlevel 1 exit /b 1

%PY% -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "BatchFolderGenerator" ^
  "app.py"

pause
