import builtins
import os
import importlib
import types

from src.agent import find_cgroup_path_for_container


def test_find_cgroup_path_for_container_monkeypatch(tmp_path, monkeypatch):
    # Create a fake cgroup path under a temp dir and monkeypatch /sys/fs/cgroup
    fake_root = tmp_path / 'sys_fs_cgroup'
    fake_root.mkdir()
    # create docker/<id>
    docker_dir = fake_root / 'docker'
    docker_dir.mkdir()
    cid = 'deadbeef'
    (docker_dir / cid).mkdir()

    # monkeypatch os.path.exists to check our fake root first
    real_exists = os.path.exists

    def fake_exists(path):
        # if path starts with /sys/fs/cgroup map to our fake_root
        if path.startswith('/sys/fs/cgroup'):
            rel = path[len('/sys/fs/cgroup'):].lstrip('/')
            p = fake_root / rel
            return p.exists()
        return real_exists(path)

    monkeypatch.setattr(os.path, 'exists', fake_exists)

    mapped = find_cgroup_path_for_container(cid)
    assert mapped in ('docker/' + cid, cid)
