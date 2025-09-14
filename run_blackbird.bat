@echo off
REM Script to find Blackbird in PATH and execute it with a username
REM Usage: run_blackbird.bat <username>

set USERNAME=%1

if "%USERNAME%"=="" (
    echo Error: No username provided
    echo Usage: %0 ^<username^>
    exit /b 1
)

REM Try to find blackbird in PATH
where blackbird >nul 2>&1
if %errorlevel%==0 (
    set BLACKBIRD_PATH=blackbird
    goto :found
)

REM Try blackbird.py
where blackbird.py >nul 2>&1
if %errorlevel%==0 (
    set BLACKBIRD_PATH=blackbird.py
    goto :found
)

REM Try python -m blackbird
python -m blackbird --help >nul 2>&1
if %errorlevel%==0 (
    set BLACKBIRD_PATH=python -m blackbird
    goto :found
)

REM Try python3 -m blackbird
python3 -m blackbird --help >nul 2>&1
if %errorlevel%==0 (
    set BLACKBIRD_PATH=python3 -m blackbird
    goto :found
)

echo Error: Blackbird not found in PATH
echo Please ensure Blackbird is installed and available in your PATH
exit /b 1

:found
echo Found Blackbird: %BLACKBIRD_PATH%
echo Searching for username: %USERNAME%

REM Execute Blackbird with the provided username and JSON output
%BLACKBIRD_PATH% --username "%USERNAME%" --json --no-update
exit /b %errorlevel%
