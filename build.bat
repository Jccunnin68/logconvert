@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
python build_executable.py

echo.
echo Build process completed!
echo Check the 'dist' folder for your executable.
pause 