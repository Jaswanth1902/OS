@echo off
echo ==========================================
echo   OS Intelligence - ML Workload Launcher
echo ==========================================

echo [1/3] Building Docker Image...
docker build -t os-ml-project -f Dockerfile.ml .
if %errorlevel% neq 0 (
    echo Build failed. Is Docker running?
    pause
    exit /b
)

echo [2/3] Starting Container...
docker run -d --name os-ml-project --cpus="2.0" --memory="2g" os-ml-project

echo [3/3] Launching Agent...
echo The Agent will run in a new window.
start "OS Agent - ML Project" python src/agent.py --docker-ids os-ml-project --interval 1

echo.
echo SUCCESS! ML Project is running.
echo Go to the Dashboard Statistics View now.
echo.
pause
