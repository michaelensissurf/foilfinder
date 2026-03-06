@echo off
cd /d "C:\Users\micha\Documents\Python\familien-dashboard\backend"
python -m uvicorn main:app --port 8000
