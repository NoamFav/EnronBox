@echo off
setlocal enabledelayedexpansion

:: Set the Enron dataset URL
set "ENRON_URL=https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
set "OUTPUT_FILE=enron_maildir.tar.gz"
set "EXTRACT_DIR=enron_maildir"

echo 🚀 Starting Enron dataset download...

:: Create the extraction directory if it doesn't exist
if not exist "%EXTRACT_DIR%" (
    mkdir "%EXTRACT_DIR%"
)

:: Download the dataset using PowerShell (since curl is limited in Windows CMD)
echo 📥 Downloading Enron email dataset...
powershell -Command "& {Invoke-WebRequest -Uri '%ENRON_URL%' -OutFile '%OUTPUT_FILE%'}"

:: Verify if the download was successful
if not exist "%OUTPUT_FILE%" (
    echo ❌ Error: Download failed!
    exit /b 1
)

echo ✅ Download complete: %OUTPUT_FILE%

:: Extract the dataset using tar (Windows 10+ includes tar)
echo 📂 Extracting dataset...
tar -xvzf "%OUTPUT_FILE%" -C "%EXTRACT_DIR%"

:: Cleanup
echo 🧹 Cleaning up...
del "%OUTPUT_FILE%"

echo 🎉 Enron dataset is ready in "%EXTRACT_DIR%"
exit /b 0
