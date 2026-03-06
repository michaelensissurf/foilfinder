Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""C:\Users\micha\Documents\Python\familien-dashboard\backend"" && python -m uvicorn main:app --port 8000", 0, False
WScript.Sleep 3000
WshShell.Run "http://localhost:8000/dashboard", 1, False
