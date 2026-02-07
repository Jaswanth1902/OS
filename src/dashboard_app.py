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
        containers = ["web-server", "db-service", "auth-worker"]
        
        while self.active:
            # Initialize node if not present
            if node_id not in GLOBAL_STATE["nodes"]:
                GLOBAL_STATE["nodes"][node_id] = {"containers": {}, "last_seen": 0}

            current_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time()
            GLOBAL_STATE["nodes"][node_id]["last_seen"] = current_time

            for c_id in containers:
                # Generate fake stats based on mode
                base_cpu = 100000 
                if self.mode == "spike" and c_id == "web-server":
                    base_cpu = 800000 + random.randint(-50000, 50000)
                elif self.mode == "attack":
                    base_cpu = 1500000 + random.randint(-100000, 200000)
                else:
                    base_cpu = 100000 + random.randint(-10000, 20000)

                # Simulated AI Prediction
                pred_cpu = base_cpu * 1.1

                # Generate Security Event if attack
                if self.mode == "attack" and random.random() < 0.1:
                    risk = "Crypto-Mining Signature Detected"
                    GLOBAL_STATE["security_scores"][c_id] = {"score": 45, "risks": [risk]}
                    log_event("SecurityScanner", f"Threat Detected in {c_id}: {risk}", "CRITICAL")
                elif self.mode == "normal":
                     GLOBAL_STATE["security_scores"][c_id] = {"score": 95, "risks": []}

                # AI Decision Logic Simulation
                if base_cpu > 1200000:
                    log_event("GovernanceEngine", f"Quarantining {c_id} due to High Load + Risk", "WARNING")
                    base_cpu = 50000 # Throttled
                
                stats = {
                    "node_id": node_id,
                    "id": c_id,
                    "cpu_usage": int(base_cpu),
                    "memory_bytes": 256 * 1024 * 1024,
                    "prediction": int(pred_cpu)
                }
                GLOBAL_STATE["nodes"][node_id]["containers"][c_id] = stats
            
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


