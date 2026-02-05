import os


def map_docker_container_to_cgroup(container_id: str):
    """Attempt to map a Docker/container ID to its cgroup path by locating the container's main PID

    Steps (best-effort):
    1. If `container_id` is already a cgroup path under `/sys/fs/cgroup`, return it.
    2. Try to import `docker` SDK and look up the container to get its PID.
    3. Read `/proc/<pid>/cgroup` and extract the cgroup path for the unified hierarchy (cgroup v2).

    Returns the cgroup path relative to `/sys/fs/cgroup`, or None if not found.
    """
    # If looks like a cgroup path already, prefer it
    if os.path.exists(os.path.join('/sys/fs/cgroup', container_id)):
        return container_id

    # Try to use docker SDK to get the PID
    try:
        import docker
    except Exception:
        return None

    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        pid = container.attrs.get('State', {}).get('Pid')
        if not pid:
            return None
        proc_path = f'/proc/{pid}/cgroup'
        if not os.path.exists(proc_path):
            return None
        with open(proc_path, 'r') as f:
            for line in f:
                # On cgroup v2 there is a single line like "0::/some/path"
                parts = line.strip().split(':', 2)
                if len(parts) == 3:
                    _, controllers, path = parts
                    # In unified cgroup v2 controllers is empty string
                    # choose the longest non-empty path
                    if path:
                        # remove leading '/'
                        return path.lstrip('/')
    except Exception:
        return None

    return None
