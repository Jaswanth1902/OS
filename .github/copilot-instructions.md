# Copilot / AI Agent Instructions for Smart OS-Level Container Manager

Purpose: Help AI coding agents quickly become productive in this repo by describing architecture, developer workflows, conventions, and concrete code examples discovered here.

**Big Picture**
- This project implements a Linux-targeted OS-level container manager that: (1) continuously monitors cgroup v2 metrics per container, (2) runs short-horizon workload predictions, and (3) issues horizontal (start/stop container) and vertical (adjust cgroup cpu/memory) actions.
- Key components in this workspace:
  - `src/agent.py`: main loop tying monitor -> predictor -> controller.
  - `src/monitor.py`: reads cgroup v2 metrics for containers and provides time-series data.
  - `src/predictor.py` / `src/ml_model.py`: lightweight forecasting model (prototype uses moving-average; replace with LSTM/TNC later).
  - `src/controller.py`: safe cgroup v2 writer which updates `cpu.max` and `memory.max` within configured bounds.
  - `examples/`: small scripts to run the prototype locally (Linux required).

**Architecture & Data Flow (concise)**
- Monitor polls cgroup filesystem (under `/sys/fs/cgroup`) and Docker API to map container IDs -> cgroup paths.
- Time-series metrics (cpu, memory usage, cpu.stat, memory.current) are fed into a predictor which emits short-horizon forecasts (seconds-to-minutes).
- Controller receives predictions and current cluster-wide capacity and computes both vertical actions (update cgroup files) and horizontal suggestions (call Docker API to scale containers). The current prototype only logs horizontal suggestions; vertical actions are applied by writing to cgroup v2 files.

**Important Assumptions & Environment**
- This code targets Linux hosts with **cgroup v2 enabled**. It is not runnable on Windows without a Linux VM/container.
- The prototype interacts with the Docker daemon via the Python `docker` package when present; fallback modes read cgroup paths for manually-managed containers.
- Editing cgroup files requires root privileges or appropriate capabilities. Tests are designed to be read-only by default.

**Developer Workflows & Commands (concrete)**
- Create and activate a Python venv, then install deps:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows (dev machine); run on Linux when deploying
pip install -r requirements.txt
```

- Run the agent locally (Linux host):

```bash
# on Linux (bash)
bash examples/run_local.sh
```

- Run unit tests (uses `pytest`):

```bash
pytest -q
```

**Project-specific Patterns & Conventions**
- cgroup v2 file writes: `cpu.max` expects either `"max"` or two integers `quota period`. The controller uses safe clamping and a staging/verification step: write to a temp file and then atomically write to the target file.
- Monitor returns metrics as records with these keys: `timestamp`, `container_id`, `cgroup_path`, `cpu_usec` (microseconds), `memory_bytes`. Use these names in predictors and controllers.
- Keep ML code isolated under `src/` so it can be swapped out. The prototype predictor exposes `fit()` and `predict(timestamp)` minimal API.
- Prefer explicit capacity checks: controller must verify global capacity before increasing per-container limits and must never set limits to `0`.

**Integration Points & External Dependencies**
- Docker Engine API (`docker` Python package) — used to map container -> cgroup paths and to start/stop containers.
- cgroup v2 filesystem (`/sys/fs/cgroup`) — for metrics and enforcement.
- Optional: Prometheus / node-exporter for richer telemetry (not included in prototype).

**Safety & Testing Notes**
- Writes to cgroup files modify OS-level resource controls — run in a controlled testbed or VM, not on production hosts.
- The prototype includes a `--dry-run` mode where controller logs actions instead of applying them.
- Tests include read-only unit tests for monitor parsing logic. Add integration tests on a disposable Linux VM for enforcement behavior.

**Where to Look Next (entry points for contributors / AI agents)**
- `src/agent.py` — start here to understand the control loop.
- `src/monitor.py` — shows how cgroup metrics are read and normalized.
- `src/controller.py` — shows safe cgroup write patterns and clamping rules.
- `examples/run_local.sh` — an executable example that runs the agent in dry-run mode.

If you need more detail on a component or want the AI to implement a specific feature (for example: LSTM trainer, Docker auto-scaling integration, or Prometheus exporter), ask for the target and I'll extend this repository with tests and runnable examples.
