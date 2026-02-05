import time
import logging
import argparse
import os
from src.monitor import CgroupMonitor
from src.controller import CgroupController
from src.predictor import MovingAveragePredictor
from src.governance import GovernanceEngine
from src.security import SecurityScanner
import requests
import json

DASHBOARD_URL = "http://localhost:8000/api/update_stats"

def report_stats(container_id, cpu, mem, prediction, node_id="local"):
    """Best-effort reporting to the dashboard."""
    try:
        data = {
            "node_id": node_id,
            "id": container_id,
            "cpu_usage": cpu,
            "memory_bytes": mem,
            "prediction": prediction
        }
        # Timeout is short to not block the control loop
        requests.post(DASHBOARD_URL, json=data, timeout=0.1)
    except Exception:
        # Dashboard might be down, ignore
        pass

def find_cgroup_path_for_container(container_id: str):
    """Heuristic mapping from a container id to a likely cgroup path under /sys/fs/cgroup.

    This tries a few common layouts and returns the first path that exists. It is conservative
    and intended for prototyping — for production use integrate with the container runtime.
    """
    candidates = [
        os.path.join('docker', container_id),
        container_id,
        f"system.slice/docker-{container_id}.scope",
        f"system.slice/containerd-{container_id}.scope",
    ]
    for c in candidates:
        full = os.path.join('/sys/fs/cgroup', c)
        if os.path.exists(full):
            return c
    return None


def run_iteration(cgroup_paths, monitor, controller, predictors, histories, scanner, governance, iteration_count, node_id="local", threshold=2000000):
    """Run a single sampling/predict/apply iteration for the given cgroup paths."""
    for p in cgroup_paths:
        sample = monitor.sample(p)
        cpu = sample['cpu_stat'].get('usage_usec', 0) if sample['cpu_stat'] else 0
        mem = sample['memory_bytes'] or 0
        histories[p].append(cpu)
        if len(histories[p]) > 1000:
            histories[p].pop(0)

        predictors[p].fit(histories[p])
        pred_cpu = predictors[p].predict()

        # Security Scan (every 10 iterations roughly, to avoid spamming Docker socket)
        # We need the container ID. 'p' is often the container ID or ends with it.
        # Simple heuristic: last part of path
        container_id = os.path.basename(p) 
        if container_id.startswith('docker-'):
            container_id = container_id[7:-6] # cleaning partial systemd names if necessary
        
        # For this prototype, if it's a long ID, treat as container ID
        if len(container_id) < 12 and p != '.':
             # Fallback
             container_id = p

        security_data = {"score": 100, "risks": []}
        if iteration_count % 10 == 0:
             security_data = scanner.scan_container(container_id)

        # Governance Check
        # We pass the 'pred_cpu' as the load metric
        action_taken = governance.evaluate(p, pred_cpu, security_data['score'], security_data['risks'])
        
        if not action_taken:
            # Normal Predictive Scaling (CPU)
            if pred_cpu > threshold:
                new_quota = int(pred_cpu * 1.2)
                logging.info("Predicted cpu for %s: %s -> set cpu.max %s", p, pred_cpu, new_quota)
                controller.set_cpu_max(p, new_quota)
            else:
                controller.set_cpu_max(p, None)
            
            # Disk IO Throttling (Prototype Policy: if IO > 10MB/s, cap at 5MB/s)
            disk_usage = sample.get('io_read_bytes', 0)
            # In a real agent, we'd need differential (rate), but here we just check raw value for prototype or mock rate
            # Let's assume 'disk_usage' is the RATE (bytes/sec) coming from monitor (in reality monitor returns total)
            # Todo: Monitor should return rate. For now, we mock the trigger.
            if disk_usage > 100 * 1024 * 1024: 
                controller.set_io_max(p, 50) # 50 MBps
            
            # Network Throttling (Policy: if "bad" behavior detected or simple quota)
            # For Phase 6 demo: we just log enabling it if a flag is present or random mock
            # controller.set_network_limit(container_id, 1000) # 1Mbps
        
        # Report to dashboard
        report_stats(p, cpu, mem, pred_cpu, node_id=node_id)


def main_loop(cgroup_paths, interval=5, dry_run=True, log_level=logging.INFO, node_id="local"):
    logging.basicConfig(level=log_level, format='[%(levelname)s] %(message)s')
    monitor = CgroupMonitor()
    controller = CgroupController(dry_run=dry_run)
    predictors = {p: MovingAveragePredictor(window=5) for p in cgroup_paths}
    histories = {p: [] for p in cgroup_paths}
    
    scanner = SecurityScanner()
    governance = GovernanceEngine(controller)
    
    iteration = 0

    try:
        while True:
            run_iteration(cgroup_paths, monitor, controller, predictors, histories, scanner, governance, iteration, node_id=node_id)
            iteration += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info('Exiting agent loop')


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='Smart OS-level container agent (prototype)')
    p.add_argument('paths', nargs='*', help='cgroup paths (relative to /sys/fs/cgroup) or container IDs')
    p.add_argument('--interval', type=int, default=5, help='Sampling interval in seconds')
    p.add_argument('--dry-run', action='store_true', help='Do not write to cgroup files, only log')
    p.add_argument('--docker-ids', action='store_true', help='Treat provided paths as Docker container IDs and try mapping')
    p.add_argument('--log-level', default='INFO', help='Logging level')
    p.add_argument('--node-id', default='local', help='Unique identifier for this agent node')
    return p.parse_args(argv)


def run_from_cli(argv=None):
    args = parse_args(argv)
    # Default path if none provided
    if not args.paths:
        cgroup_paths = ['.']
    else:
        cgroup_paths = []
        for p in args.paths:
            if args.docker_ids:
                mapped = find_cgroup_path_for_container(p)
                if mapped:
                    cgroup_paths.append(mapped)
                else:
                    logging.warning('Could not map container %s to cgroup path; using literal value', p)
                    cgroup_paths.append(p)
            else:
                cgroup_paths.append(p)

    main_loop(cgroup_paths, interval=args.interval, dry_run=args.dry_run, log_level=getattr(logging, args.log_level.upper(), logging.INFO), node_id=args.node_id)


if __name__ == '__main__':
    run_from_cli()
