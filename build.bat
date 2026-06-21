@echo off
echo ========================================
echo Video extractor by ParallaXYZ - Build
echo ========================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: .venv not found
    pause
    exit /b 1
)

echo Installing requirements...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: requirements install failed
    pause
    exit /b 1
)

echo.
echo Checking and downloading required binaries...
python download_binaries.py
if errorlevel 1 (
    echo ERROR: Binary download failed
    echo Please download binaries manually (see instructions above^)
    pause
    exit /b 1
)

echo.
echo Running automated release builder...
python create_release.py
if errorlevel 1 (
    echo ERROR: Release creation failed
    pause
    exit /b 1
)

echo.
echo Done.
pause