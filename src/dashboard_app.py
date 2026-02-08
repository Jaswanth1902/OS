import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from typing import Dict, List

# Prototype imports - in a real app these would be properly injected
try:
    from src.agent import CgroupMonitor, CgroupController
    from src.security import SecurityScanner
except ImportError:
    # Fallback for running directly from src/
    from .agent import CgroupMonitor, CgroupController
    from .security import SecurityScanner

app = FastAPI(title="Smart OS Container Manager")

# Setup templates
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "templates")
if not os.path.exists(template_dir):
    os.makedirs(template_dir)

templates = Jinja2Templates(directory=template_dir)

# Global state
# In production, use Redis or a proper database
# Structure: { "node_1": { "containers": {...}, "last_seen": timestamp }, ... }
GLOBAL_STATE = {
    "nodes": {}
}

scanner = SecurityScanner()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    """Returns the aggregated stats from all nodes."""
    return GLOBAL_STATE["nodes"]

@app.post("/api/update_stats")
async def update_stats(stats: Dict):
    """
    Internal endpoint for the Agent to push updates.
    Payload expected: { "node_id": "host1", "containers": [ ... ] } or single container update
    For backward compatibility, we support single update if no node_id.
    """
    node_id = stats.get("node_id", "local")
    
    if node_id not in GLOBAL_STATE["nodes"]:
        GLOBAL_STATE["nodes"][node_id] = {"containers": {}, "last_seen": 0}
    
    # Handle single container update (agent pushing one by one)
    container_id = stats.get("id")
    if container_id:
        GLOBAL_STATE["nodes"][node_id]["containers"][container_id] = stats
    
    GLOBAL_STATE["nodes"][node_id]["last_seen"] = asyncio.get_event_loop().time()
    
    return {"status": "ok"}

@app.get("/api/security/{container_id}")
async def scan_container(container_id: str, background_tasks: BackgroundTasks):
    """Trigger a security scan for a container."""
    # Run synchronously for prototype simplicity, or background if heavy
    result = scanner.scan_container(container_id)
    GLOBAL_STATE["security_scores"][container_id] = result
    return result

@app.get("/api/security_cache")
async def get_security_cache():
    return GLOBAL_STATE["security_scores"]

@app.get("/api/run_evaluation")
async def run_evaluation(background_tasks: BackgroundTasks):
    """
    Triggers an evaluation run. 
    In specific implementation, this would invoke src.evaluation.
    Here we mock it by running the self-test logic of evaluation suite and returning the file content.
    """
    from src.evaluation import EvaluationSuite
    import csv 
    import io

    # Run synchronously for this prototype demo
    evaluator = EvaluationSuite(None)
    evaluator.run_scenario("Web Server Load", 20, "static")
    evaluator.run_scenario("Web Server Load", 20, "dynamic")
    evaluator.export_csv("evaluation_report.csv")
    
    # Read CSV and return
    data = []
    with open("evaluation_report.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            
from datetime import datetime
from collections import deque
import random
import threading
import time

# Event Log (Circular Buffer)
EVENT_LOG = deque(maxlen=50)

def log_event(source, message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    event = {
        "timestamp": timestamp,
        "source": source,
        "message": message,
        "level": level
    }
    EVENT_LOG.appendleft(event)

# Simulation Engine
class SimulationEngine:
    def __init__(self):
        self.active = False
        self.thread = None
        self.mode = "normal"  # normal, spike, attack
    
    def start(self):
        if self.active: return
        self.active = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        log_event("Simulator", "simulation_started", "SUCCESS")

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=1.0)
        log_event("Simulator", "simulation_stopped", "WARNING")

    def set_mode(self, mode):
        self.mode = mode
        log_event("Simulator", f"mode_switched_to_{mode.upper()}", "INFO")

    def _run_loop(self):
        node_id = "sim-node-01"
        container_id = "ML-Project-Container"
        
        start_time = time.time()
        
        while self.active:
            # Lifecycle Management (2 Minute Cycle)
            elapsed = time.time() - start_time
            if elapsed > 130: 
                start_time = time.time() # Loop the demo
                elapsed = 0
                log_event("GovernanceEngine", f"Restarting Demo Cycle for {container_id}", "INFO")

            # Initialize node if not present
            if node_id not in GLOBAL_STATE["nodes"]:
                GLOBAL_STATE["nodes"][node_id] = {"containers": {}, "last_seen": 0}

            current_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time()
            GLOBAL_STATE["nodes"][node_id]["last_seen"] = current_time

            # Default Low Resources
            cpu_usage = 50000  # 5%
            mem_usage = 128 * 1024 * 1024 # 128MB
            
            # 1. Initialization (0-10s)
            if elapsed < 10:
                cpu_usage = 100000 + random.randint(-10000, 10000)
                if int(elapsed) % 5 == 0:
                    log_event("Orchestrator", f"Allocating initial resources for {container_id}", "INFO")
            
            # 2. Data Loading (10-40s)
            elif elapsed < 40:
                # Memory Ramps Up
                progress = (elapsed - 10) / 30
                mem_usage = 128 * 1024 * 1024 + (progress * 2 * 1024 * 1024 * 1024) # Up to 2GB
                cpu_usage = 300000 + random.randint(-50000, 50000)
                if int(elapsed) == 20:
                     log_event("ML-Engine", "Loading dataset into memory (1.5GB)...", "INFO")
            
            # 3. Training (40-100s) - High CPU
            elif elapsed < 100:
                cpu_usage = 2500000 + random.randint(-200000, 200000) # 2.5 Cores
                mem_usage = 2.2 * 1024 * 1024 * 1024 # Steady High Mem
                
                if int(elapsed) == 45:
                    log_event("GovernanceEngine", f"Detected high load in {container_id}. Increasing CPU limits dynamically.", "WARNING")
                if int(elapsed) == 70:
                    log_event("AutoScaler", f"Scaling out calculation nodes for {container_id}", "SUCCESS")

            # 4. Completion (100-120s)
            elif elapsed < 120:
                cpu_usage = 200000 # Drop
                mem_usage = 512 * 1024 * 1024 
                if int(elapsed) == 101:
                    log_event("ML-Engine", "Training complete. Model saved.", "SUCCESS")
                if int(elapsed) == 105:
                    log_event("GovernanceEngine", "Releasing unused resources back to pool.", "INFO")

            # Prediction is slightly ahead of actual
            pred_cpu = cpu_usage * 1.05

            stats = {
                "node_id": node_id,
                "id": container_id,
                "cpu_usage": int(cpu_usage),
                "memory_bytes": int(mem_usage),
                "prediction": int(pred_cpu)
            }
            GLOBAL_STATE["nodes"][node_id]["containers"][container_id] = stats
            
            # Security Score (Healthy for this demo unless explicitly attacked)
            GLOBAL_STATE["security_scores"][container_id] = {"score": 98, "risks": []}

            time.sleep(1)

sim_engine = SimulationEngine()

@app.get("/api/events")
async def get_events():
    return list(EVENT_LOG)

@app.post("/api/simulation/{action}")
async def control_simulation(action: str, mode: str = "normal"):
    if action == "start":
        sim_engine.start()
    elif action == "stop":
        sim_engine.stop()
    elif action == "mode":
        sim_engine.set_mode(mode)
    return {"status": "ok", "active": sim_engine.active, "mode": sim_engine.mode}

@app.on_event("startup")
async def startup_event():
    log_event("System", "Dashboard Initialized", "SUCCESS")


