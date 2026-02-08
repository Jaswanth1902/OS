#!/bin/bash

echo "Stopping os-ml-project container..."
sudo docker rm -f os-ml-project

if [ -f agent_pid.txt ]; then
    AGENT_PID=$(cat agent_pid.txt)
    echo "Stopping Agent (PID: $AGENT_PID)..."
    kill $AGENT_PID
    rm agent_pid.txt
else
    echo "Agent PID file not found. Attempting to find process..."
    pkill -f "src/agent.py"
fi

echo ""
echo "Done."
