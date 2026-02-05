# Deployment Guide - Smart OS-Level Container Manager

This guide details how to deploy the project on a Linux Machine (e.g., Ubuntu 22.04) and securely access the dashboard from a remote machine.

## Prerequisites

1.  **Linux OS**: Recommended Ubuntu 20.04 or later.
2.  **Cgroup v2**: Must be enabled.
    *   Check with: `stat -fc %T /sys/fs/cgroup/`
    *   Output should be `cgroup2fs`.
3.  **Docker**: Installed and running.
    *   `curl -fsSL https://get.docker.com | sh`
4.  **Python 3.9+**: Installed.

## Step 1: Clone and Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/smart-os-manager.git
    cd smart-os-manager
    ```

2.  **Create Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Step 2: Running the Services

You need to run two components: the **Dashboard** (Backend) and the **Control Agent**.

### 1. Start the Dashboard (Term 1)
The dashboard serves the UI and API.
```bash
# Activate venv if not active
source .venv/bin/activate

# Run Uvicorn Server on localhost
uvicorn src.dashboard_app:app --host 127.0.0.1 --port 8000
```
*Note: We bind to `127.0.0.1` for security so it is NOT exposed to the public internet directly.*

### 2. Start the Agent (Term 2)
The agent monitors containers and applies limits.
```bash
# Activate venv
source .venv/bin/activate

# Run Agent (replace <CONTAINER_ID> with actual ID or remove args monitors all if implemented)
# To monitor specific container:
python -m src.agent <container_id> --docker-ids --node-id linux-node-1
```
*(Remove `--dry-run` to enable actual resource throttling)*

## Step 3: Secure Remote Access

To view the dashboard from your local machine (e.g., your laptop) without exposing port 8000 to the public internet, use an **SSH Tunnel**.

### On Your Local Machine (Another Agent's PC):
Run this command in your terminal:
```bash
ssh -L 8000:127.0.0.1:8000 user@<your-linux-server-ip>
```
*Replace `user` and `<your-linux-server-ip>` with your credentials.*

### View the Dashboard
1.  Open your browser on your local machine.
2.  Navigate to: **[http://localhost:8000](http://localhost:8000)**
3.  You will see the **Sunset Orange Glassmorphic UI** securely tunneled from the server.

## Troubleshooting

-   **Permission Denied**: The Agent needs root privileges to write to `/sys/fs/cgroup`. Run with `sudo`:
    ```bash
    sudo .venv/bin/python -m src.agent ...
    ```
-   **Missing Cgroups**: Ensure your container runtime (Docker) is configured to use `systemd` cgroup driver.
    ```bash
    cat /etc/docker/daemon.json
    # Should contain: { "exec-opts": ["native.cgroupdriver=systemd"] }
    ```
