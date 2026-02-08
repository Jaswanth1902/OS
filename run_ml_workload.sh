#!/bin/bash

echo "=========================================="
echo "  OS Intelligence - ML Workload Launcher"
echo "=========================================="

echo "[1/3] Building Docker Image..."
sudo docker build -t os-ml-project -f Dockerfile.ml .
if [ $? -ne 0 ]; then
    echo "Build failed. Is Docker running?"
    exit 1
fi

echo "[2/3] Starting Container..."
sudo docker run -d --name os-ml-project --cpus="2.0" --memory="2g" os-ml-project

echo "[3/3] Launching Agent..."
# Run in background and save PID
python3 src/agent.py --docker-ids os-ml-project --interval 1 &
AGENT_PID=$!
echo $AGENT_PID > agent_pid.txt

echo ""
echo "SUCCESS! ML Project is running."
echo "Agent PID: $AGENT_PID (Saved to agent_pid.txt)"
echo "Go to the Dashboard Statistics View now."
echo ""
echo "To stop, run: ./stop_ml_workload.sh"
