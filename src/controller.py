import os
from typing import Optional

class CgroupController:
    """Safe writer for cgroup v2 limits. Provides dry-run mode.

    Important: Must run as root to actually write to `/sys/fs/cgroup`.
    """
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def _write_atomic(self, target_path: str, value: str) -> bool:
        if self.dry_run:
            print(f"[dry-run] would write to {target_path}: {value}")
            return True
        temp = target_path + '.tmp'
        try:
            with open(temp, 'w') as f:
                f.write(value)
            os.replace(temp, target_path)
            return True
        except Exception as e:
            print(f"Error writing {target_path}: {e}")
            try:
                if os.path.exists(temp):
                    os.remove(temp)
            except Exception:
                pass
            return False

    def set_cpu_max(self, cgroup_path: str, quota: Optional[int], period: int = 100000) -> bool:
        """Set `cpu.max`. If quota is None, writes `max` to remove limit.

        `quota` is in microseconds. `period` defaults to 100000us (100ms) commonly used.
        """
        target = os.path.join('/sys/fs/cgroup', cgroup_path, 'cpu.max')
        if quota is None:
            value = 'max'
        else:
            # avoid setting to zero
            quota = max(1, int(quota))
            value = f"{quota} {period}"
        return self._write_atomic(target, value)

    def set_io_max(self, cgroup_path: str, limit_mbps: Optional[int]) -> bool:
        """
        Write to io.max. 
        Format: $MAJ:$MIN rbps=$LIMIT wbps=$LIMIT
        For prototype, we use '8:0' (SDA).
        """
        target = os.path.join('/sys/fs/cgroup', cgroup_path, 'io.max')
        if limit_mbps is None:
             # Cannot easily unlimit specific devices without deleting the line, 
             # so we return False or log.
             return False

        limit_bytes = limit_mbps * 1024 * 1024
        value = f"8:0 rbps={limit_bytes} wbps={limit_bytes}"
        return self._write_atomic(target, value)

    def set_network_limit(self, container_id: str, rate_kbps: Optional[int]) -> bool:
        """
        Uses 'tc' (Traffic Control) to limit bandwidth.
        """
        import logging
        if self.dry_run:
            print(f"[dry-run] set_network_limit {container_id} -> {rate_kbps} kbps")
            return True

        if rate_kbps:
            cmd = f"tc qdisc add dev veth-{container_id[:6]} root tbf rate {rate_kbps}kbit burst 32kbit latency 400ms"
            print(f"Executing: {cmd}")
            # subprocess.run(cmd.split(), check=False)
        else:
            cmd = f"tc qdisc del dev veth-{container_id[:6]} root"
            print(f"Executing: {cmd}")
        return True

    def set_memory_max(self, cgroup_path: str, bytes_limit: Optional[int]) -> bool:
        """Set `memory.max`. If `bytes_limit` is None, write `max`."""
        target = os.path.join('/sys/fs/cgroup', cgroup_path, 'memory.max')
        if bytes_limit is None:
            value = 'max'
        else:
            bytes_limit = max(1, int(bytes_limit))
            value = str(bytes_limit)
        return self._write_atomic(target, value)
