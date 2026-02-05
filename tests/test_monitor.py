import pytest
from src.monitor import CgroupMonitor


def test_read_nonexistent_cgroup():
    mon = CgroupMonitor()
    # Should return None rather than raising
    assert mon.read_cpu_stat('this-path-does-not-exist') is None
    assert mon.read_memory_current('this-path-does-not-exist') is None
