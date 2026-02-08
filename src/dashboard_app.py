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
        bg_containers = ["web-server", "db-service", "auth-worker"]
        ml_container_id = "os-ml-project"
        
        start_time = time.time()
        
        while self.active:
            # 1. Background Noise (Simulated Containers)
            if node_id not in GLOBAL_STATE["nodes"]:
                GLOBAL_STATE["nodes"][node_id] = {"containers": {}, "last_seen": 0}

            current_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time()
            GLOBAL_STATE["nodes"][node_id]["last_seen"] = current_time

            for c_id in bg_containers:
                # Standard random load for background services
                base_cpu = 100000 + random.randint(-10000, 20000)
                if self.mode == "spike" and c_id == "web-server": base_cpu += 700000
                if self.mode == "attack": base_cpu += 1400000

                GLOBAL_STATE["nodes"][node_id]["containers"][c_id] = {
                    "node_id": node_id,
                    "id": c_id,
                    "cpu_usage": int(base_cpu),
                    "memory_bytes": 256 * 1024 * 1024,
                    "prediction": int(base_cpu * 1.1)
                }
                
                # Security Score for bg apps
                score = 95 if self.mode != "attack" else (45 if c_id == "web-server" and random.random() < 0.1 else 95)
                GLOBAL_STATE["security_scores"][c_id] = {"score": score, "risks": ["Potential Threat"] if score < 50 else []}
                if score < 50: log_event("SecurityScanner", f"Threat Detected in {c_id}", "CRITICAL")

            # 2. Check for Real Activity (os-ml-project)
            ml_active = False
            for nid in GLOBAL_STATE["nodes"]:
                if ml_container_id in GLOBAL_STATE["nodes"][nid]["containers"]:
                    ml_active = True
                    break
            
            # If the Real Docker Container is running, synchronize our story logs with it
            if ml_active:
                elapsed = time.time() - start_time
                if elapsed > 130: 
                    start_time = time.time() # Loop the demo cycle logs
                    elapsed = 0
                    log_event("GovernanceEngine", f"Restarting Demo Logic for {ml_container_id}", "INFO")

                # 0-10s: Init
                if elapsed < 10:
                    if int(elapsed) % 5 == 0:
                        log_event("Orchestrator", f"Allocating initial resources for {ml_container_id}", "INFO")
                # 10-40s: Data Loading
                elif elapsed < 40:
                    if int(elapsed) == 20:
                         log_event("ML-Engine", "Loading dataset into memory (1.5GB)...", "INFO")
                # 40-100s: Training
                elif elapsed < 100:
                    if int(elapsed) == 45:
                        log_event("GovernanceEngine", f"Detected high load in {ml_container_id}. Increasing CPU limits dynamically.", "WARNING")
                    if int(elapsed) == 70:
                        log_event("AutoScaler", f"Scaling out calculation nodes for {ml_container_id}", "SUCCESS")
                # 100-120s: Completion
                elif elapsed < 120:
                    if int(elapsed) == 101:
                        log_event("ML-Engine", "Training complete. Model saved.", "SUCCESS")
                    if int(elapsed) == 105:
                        log_event("GovernanceEngine", "Releasing unused resources back to pool.", "INFO")
            else:
                # Reset log timer if container disappears
                start_time = time.time()

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


