@echo off
setlocal enabledelayedexpansion

:: Set the Enron dataset URL
set "ENRON_URL=https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
set "OUTPUT_FILE=enron_maildir.tar.gz"

echo 🚀 Starting Enron dataset download...

:: Download the dataset using PowerShell (since curl is limited in Windows CMD)
echo 📥 Downloading Enron email dataset...
powershell -Command "& {Invoke-WebRequest -Uri '%ENRON_URL%' -OutFile '%OUTPUT_FILE%'}"

:: Verify if the download was successful
if not exist "%OUTPUT_FILE%" (
    echo ❌ Error: Download failed!
    exit /b 1
)

echo ✅ Download complete: %OUTPUT_FILE%

:: Extract directly into current directory
echo 📂 Extracting dataset...
tar -xvzf "%OUTPUT_FILE%"

:: Check if maildir folder was extracted
if not exist "maildir" (
    echo ❌ Extraction failed or 'maildir' not found!
    exit /b 1
)

:: Cleanup
echo 🧹 Cleaning up...
del "%OUTPUT_FILE%"

echo 🎉 Enron dataset is ready in "maildir\"
exit /b 0
