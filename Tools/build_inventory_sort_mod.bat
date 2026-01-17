@echo off
echo ============================================================
echo     MINECRAFT DUNGEONS - INVENTORY SORT MOD BUILDER
echo ============================================================
echo.

cd /d "%~dp0\.."

echo [1] Running inventory sort mod setup...
python Tools\py\inventory_sort_mod.py
if errorlevel 1 (
    echo Error running mod setup!
    pause
    exit /b 1
)

echo.
echo [2] Creating mod package...
call package.bat
if errorlevel 1 (
    echo Error creating package!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo     MOD BUILD COMPLETE!
echo ============================================================
echo.
echo The mod has been packaged. Check your ~mods folder.
echo.
echo If the sort functionality doesn't work in-game, you'll need
echo to use UAssetGUI or UE4 Editor to complete the integration.
echo.
pause
