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
            
    return data
