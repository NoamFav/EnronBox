@echo off
@echo off
echo 📦 Installing Python requirements...
pip install -r requirements.txt

echo 🧠 Running post-install script...
python scripts\postinstall.py

echo ✅ Setup complete!
pause
