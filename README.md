Smart OS-Level Container Manager (prototype)

This repository contains a minimal prototype for a Linux-targeted OS-level container manager that:
- Monitors per-container cgroup v2 metrics
- Runs short-horizon predictions (prototype predictor included)
- Applies vertical scaling via cgroup v2 writes (dry-run by default)

Requirements
- Linux host with cgroup v2 enabled
- Python 3.9+
- Root privileges (for applying cgroup changes) or use dry-run

Quickstart (Linux)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash examples/run_local.sh
```

Files of interest
- `src/agent.py` - main loop
- `src/monitor.py` - cgroup reading helpers
- `src/predictor.py` - lightweight predictor API
- `src/controller.py` - cgroup writer and safety checks
 - `src/docker_utils.py` - helper to map Docker container IDs to cgroup paths (best-effort)
 - `src/ml_model.py` - pluggable ML model wrapper (uses scikit-learn RandomForest)
 - `scripts/train_model.py` - example script that trains a small model on synthetic data
 - `.github/workflows/ci.yml` - GitHub Actions CI config (runs pytest)

Safety
- Do not run the enforcement mode on production hosts. Use a VM or testbed.

Quick commands

- Install dependencies (Linux/WSL/VM):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run the agent in dry-run (treats args as cgroup paths):

```bash
python -m src.agent <cgroup-path> --dry-run
```

- Try mapping Docker container IDs (best-effort):

```bash
python -m src.agent <container-id> --docker-ids --dry-run
```

- Train the simple model on synthetic data:

```bash
python scripts/train_model.py
```

- Run tests:

```bash
pytest -q
```
