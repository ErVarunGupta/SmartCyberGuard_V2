@echo off
cd /d %~dp0

echo Starting SmartGuard Dashboard...

call venv\Scripts\activate

python -m streamlit run app.py

pause