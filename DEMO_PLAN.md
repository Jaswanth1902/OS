# Showcase Demo Plan: "The ML Stress Test"

## 1. The Narrative
We will demonstrate that the **OS Intelligence Agent** is "Universal". It doesn't need custom integrations; it automatically detects, monitors, and governs *any* Linux workload you throw at it—even a heavy Machine Learning training job.

## 2. Setup (Pre-Show)
1.  **Start the Brain (Dashboard)**
    ```bash
    uvicorn src.dashboard_app:app --host 0.0.0.0 --port 8000
    ```
2.  **Stop Simulation**: Ensure the "Showcase Mode" is **OFF** in the dashboard so the view is empty/clean.
3.  **Start the Eyes (Agent)**
    Ensure your agent is running and watching Docker.
    ```bash
    # In a separate terminal
    python src/agent.py --node-id "PROD-SERVER-01"
    ```

## 3. The "Surprise" Workload
*You (The Presenter) will run a never-before-seen container live.*

### A. The Setup (Your Custom ML Job)
You mentioned you will package a Python script that:
1.  **Cleans Data**: Loops through a large Dataset (High CPU).
2.  **Trains Model**: Fits a Model (High CPU + High Memory).
3.  **Completes**: Exits or sleeps.

### B. The Execution
Run your custom container:
```bash
docker run --rm --name live-ml-training <your-image-name>
```

## 4. What to Show on Dashboard (The "Wow" Moment)
1.  **Auto-Discovery**: Point at the **"Active Containers"** list.
    *   *Script*: "Notice I didn't configure anything. The system instantly detected `live-ml-training`."
2.  **Real-Time Telemetry**:
    *   **Data Cleaning Phase**: "Look at the CPU graph climbing as we scrub the data."
    *   **Training Phase**: "Now watch the Memory usage spike. The model is loading the dataset into RAM."
3.  **Intelligence Logs**:
    *   If the usage gets very high, check the **Intelligence/Logs** section.
    *   *Script*: "The AI sees this spike. It's logging the resource consumption in real-time."

## 5. Conclusion
"This proves our system provides **Zero-Touch Observability** for any application, from simple web servers to complex AI pipelines."
