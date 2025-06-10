@echo off
setlocal enabledelayedexpansion

echo 🚀 Generating SQLite database...
python apps\SQLite_db\generate_db.py
if errorlevel 1 (
    echo ❌ Database generation failed!
    exit /b 1
)
echo ✅ Database generated!
