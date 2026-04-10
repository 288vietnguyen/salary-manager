@echo off
setlocal

:: Project root is one level up from this script
set ROOT=%~dp0..

echo [1/4] Checking Python...
where python >nul 2>&1 || (echo ERROR: Python not found. Install from https://www.python.org/downloads/ && pause && exit /b 1)

echo [2/4] Installing / updating dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "%ROOT%\requirements.txt"
python -m pip install --quiet pyinstaller

echo [3/4] Downloading EasyOCR models...
set MODELS_DIR=%ROOT%\backend\models
if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"

if not exist "%MODELS_DIR%\craft_mlt_25k.pth" (
    echo   -^> craft_mlt_25k.pth
    curl -L -k -o "%TEMP%\craft.zip" "https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip"
    powershell -command "Expand-Archive -Path '%TEMP%\craft.zip' -DestinationPath '%MODELS_DIR%' -Force"
    del "%TEMP%\craft.zip"
)

if not exist "%MODELS_DIR%\latin_g2.pth" (
    echo   -^> latin_g2.pth
    curl -L -k -o "%TEMP%\latin.zip" "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/latin_g2.zip"
    powershell -command "Expand-Archive -Path '%TEMP%\latin.zip' -DestinationPath '%MODELS_DIR%' -Force"
    del "%TEMP%\latin.zip"
)

echo [4/4] Building executable...
python -m PyInstaller "%ROOT%\build\salary-manager.spec" ^
    --distpath "%ROOT%\dist" ^
    --workpath "%ROOT%\build\_tmp" ^
    --noconfirm

if errorlevel 1 (
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Build complete: dist\SalaryManager\SalaryManager.exe
echo  OCR models are downloaded automatically on first use.
echo ============================================================
pause
