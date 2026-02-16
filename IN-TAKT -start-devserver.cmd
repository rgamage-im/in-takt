@echo off
REM Launch Ubuntu (WSL) and run Django dev server
REM wsl.exe -d Ubuntu -- bash -lc "cd ~/projects/budget-forecaster && if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi && python manage.py runserver 0.0.0.0:8001"
wsl.exe -d Ubuntu -- bash -lc "cd ~/projects/in-takt && venv/bin/python manage.py runserver 0.0.0.0:8080"

