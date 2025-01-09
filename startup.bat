@echo off

:: Launch the backend in a new command window
echo Starting Flask backend...
start cmd /k "cd DeepTald_back_end && .venv\Scripts\activate && .venv\Scripts\python.exe source/server.py"

:: Launch the frontend in a new command window
echo Starting Flutter frontend...
start cmd /k "cd DeepTald_front_end/web && python -m http.server 8000"

:: Pause to keep this window open in case there are errors
pause
