# OS Container Management - Showcase Demo Plan

## goal
Demonstrate a "Zero-Touch" Intelligent Operating System that manages container resources autonomously.

## Prerequisities
1.  **Windows with Docker Desktop** running.
2.  Python 3.9+ installed.
3.  Git Bash or PowerShell terminal.
4.  Port `8000` is free.

## Phase 1: Setup (Before Audience Arrives)
1.  Open Terminal in `c:\Users\jaswa\Downloads\OS` (or Linux path).
2.  Start the Dashboard:
    ```bash
    # Windows
    uvicorn src.dashboard_app:app --port 8000
    # Linux
    python3 -m uvicorn src.dashboard_app:app --port 8000
    ```
3.  Open Browser to `http://localhost:8000`.

## Phase 2: The Pitch (Simulation Lab)
"We have built an OS that watches containers like a hawk."

1.  Navigate to **Simulation Lab**.
2.  Explain: "first, let's start the background services."
3.  Click **"Start Simulation"**.
    *   3 simulated containers (`web-server`, `db-service`, `auth-worker`) appear.
    *   Show **Statistics** view: It shows aggregate data for these services.

## Phase 3: The Real Stuff (Manual Launch)
"Now, let's run a **Real Machine Learning Project** on this local machine."

1.  Open a new Terminal.
2.  Run the workload script:
    ```cmd
    # Windows
    run_ml_workload.bat
    
    # Linux
    chmod +x run_ml_workload.sh
    ./run_ml_workload.sh
    ```
    *   *Explain:* "This builds a Docker container and launches our Agent."
    *   A new window will pop up (The Agent).

3.  **Switch to Dashboard**:
    *   **Auto-Detection**: The Dashboard *immediately* updates.
    *   **Statistics View**: Now focuses EXCLUSIVELY on `os-ml-project`.
    *   **Graphs**: Watch the Real CPU/Memory spikes.

## Phase 4: The Story (2-Minute Lifecycle)
1.  **0-10s (Initialization)**: Low usage.
2.  **10-40s (Data Loading)**: Memory graph rises (Loading 1.5GB).
3.  **40-100s (Training)**: CPU spikes to 100%. 
    *   **Intelligence View**: Logs appear: *"Detected high load... Increasing limits"*.
4.  **100s+ (Completion)**: Usage drops.

## Phase 5: Cleanup
1.  Run cleanup script:
    ```cmd
    # Windows
    stop_ml_workload.bat
    
    # Linux
    ./stop_ml_workload.sh
    ```
2.  Click **"Stop"** in Simulation Lab.
