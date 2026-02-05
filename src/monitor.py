import os
import time
from typing import Dict, Optional

class CgroupMonitor:
    """Small helper to read minimal cgroup v2 stats for a container.

    Methods are intentionally simple and tolerant so unit tests can run on non-Linux hosts.
    """

    def __init__(self):
        pass

    def read_cpu_stat(self, cgroup_path: str) -> Optional[Dict[str, int]]:
        """Read `/sys/fs/cgroup/<path>/cpu.stat` and return dict with usage_usec."""
        path = os.path.join('/sys/fs/cgroup', cgroup_path, 'cpu.stat')
        try:
            with open(path, 'r') as f:
                data = f.read().splitlines()
        except Exception:
            return None
        out = {}
        for line in data:
            k, v = line.split()
            out[k] = int(v)
        return out

    def read_memory_current(self, cgroup_path: str) -> Optional[int]:
        path = os.path.join('/sys/fs/cgroup', cgroup_path, 'memory.current')
        try:
            with open(path, 'r') as f:
                return int(f.read().strip())
        except Exception:
            return None

    def sample(self, cgroup_path: str) -> Dict:
        now = time.time()
        cpu = self.read_cpu_stat(cgroup_path) or {}
        mem = self.read_memory_current(cgroup_path)
        return {
            'timestamp': now,
            'cgroup_path': cgroup_path,
            'cpu_stat': cpu,
            'memory_bytes': mem,
            'io_read_bytes': self.read_io_stat(cgroup_path),
            # Network stat would ideally require container runtime introspection or /proc/net/dev of the namespace
            # For prototype, we skip implementation or mock it
            'net_rx_bytes': 0 
        }

    def read_io_stat(self, cgroup_path: str) -> int:
        """Reads io.stat for the given cgroup and returns total read+write bytes."""
        path = os.path.join('/sys/fs/cgroup', cgroup_path, 'io.stat')
        total_bytes = 0
        try:
            with open(path, 'r') as f:
                data = f.read().splitlines()
            # Format: 8:0 rbytes=100 wbytes=200 ...
            for line in data:
                parts = line.split()
                for p in parts:
                    if p.startswith('rbytes=') or p.startswith('wbytes='):
                        total_bytes += int(p.split('=')[1])
        except Exception:
            pass
        return total_bytes
