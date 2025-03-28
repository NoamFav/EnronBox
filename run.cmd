@echo off
setlocal

REM Colors for output (just using echo, since Windows CMD has no ANSI by default)
set MAX_EMAILS=5000

REM Help menu
IF "%~1"=="--help" (
    echo Usage: run.cmd [--max_emails N]
    echo.
    echo Options:
    echo   --max_emails N     Load N emails from the Enron dataset (default: 5000)
    exit /b 0
)

REM Parse arguments
:parse_args
IF "%~1"=="" GOTO after_parse
IF "%~1"=="--max_emails" (
    SET MAX_EMAILS=%~2
    SHIFT
) ELSE (
    echo ❌ Unknown argument: %~1
    exit /b 1
)
SHIFT
GOTO parse_args

:after_parse

REM Install dependencies
echo 📦 Checking Python dependencies...
pip install -r requirements.txt >nul

REM Run the app
echo 🚀 Launching Enron Email Intelligence Shell...
python src\main.py --max_emails %MAX_EMAILS%

endlocal