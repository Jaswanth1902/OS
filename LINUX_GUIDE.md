# OS Intelligence - Linux Deployment Guide

## Prerequisites
1.  **Ubuntu 20.04+** (Recommended) or any modern Linux distro.
2.  **Docker** installed and running (`sudo systemctl status docker`).
    - Add your user to docker group: `sudo usermod -aG docker $USER`.
3.  **Python 3.9+** installed (`python3 --version`).
4.  **Git** installed.

## 1. Installation

### Clone Request
```bash
git clone <your-repo-url>
cd OS
```

### Install Dependencies
```bash
# It runs best in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, manually install: `pip install fastapi uvicorn docker requests psutil`)*

## 2. Running the Dashboard (Terminal 1)
This servers the UI and the API.

```bash
# In OS/ directory
source venv/bin/activate
python3 -m uvicorn src.dashboard_app:app --host 0.0.0.0 --port 8000
```
- Open Browser to: `http://localhost:8000` (or your server IP).

## 3. Running the Simulation Lab
1.  Navigate to **Simulation Lab** in the browser.
2.  Click **"Start Simulation"**.
3.  You should see 3 simulated containers (`web-server`, `db-service`, etc.) appear.

## 4. Running the Real ML Project (Terminal 2)
This launches the real Docker container and the monitoring Agent.

```bash
# In OS/ directory
source venv/bin/activate

# Make script executable (first time only)
chmod +x run_ml_workload.sh

# Run it
./run_ml_workload.sh
```

**Expected Output:**
```
[1/3] Building Docker Image...
[2/3] Starting Container...
[3/3] Launching Agent...
SUCCESS! ML Project is running.
Agent PID: 12345
```

## 5. Verify in Dashboard
1.  Go to **Statistics View**.
2.  The graphs should automatically switch to show **`os-ml-project`**.
3.  Watch the 2-minute lifecycle:
    - **0-10s**: Low usage.
    - **10-40s**: Memory climb (Loading Data).
    - **40-100s**: CPU Spike (Training).
    - **100s+**: Cool down.

## 6. Cleanup
When finished:

```bash
# Terminate the workload and agent
./stop_ml_workload.sh
```

Then click **"Stop"** in the Simulation Lab UI.

## Troubleshooting
- **Permission Denied**: Ensure you used `chmod +x *.sh`.
- **Docker Errors**: Ensure `sudo docker ps` works. The scripts use `sudo` by default for Docker commands to be safe, but if you configured non-root access, you can edit the scripts to remove `sudo`.
- **Port 8000 Busy**: Change port in Step 2 (`--port 8001`) and update the URL.
