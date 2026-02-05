import logging
try:
    import docker
except ImportError:
    docker = None

class SecurityScanner:
    """Static analysis of container configurations for security risks."""

    def __init__(self):
        self.client = None
        if docker:
            try:
                self.client = docker.from_env()
            except Exception as e:
                logging.warning(f"Could not connect to Docker daemon: {e}")

    def scan_container(self, container_id: str) -> dict:
        """
        Scans a container for security risks.
        Returns a dict containing:
        - score: 0-100 (100 is secure)
        - risks: List of strings describing issues
        """
        if not self.client:
            return {"score": 0, "risks": ["Docker client not available"], "details": {}}

        try:
            container = self.client.containers.get(container_id)
            attrs = container.attrs
        except Exception as e:
            return {"score": 0, "risks": [f"Could not fetch container info: {e}"], "details": {}}

        score = 100
        risks = []
        details = {}

        # Check 1: Privileged Mode
        privileged = attrs.get('HostConfig', {}).get('Privileged', False)
        details['privileged'] = privileged
        if privileged:
            score -= 40
            risks.append("Container is running in Privileged mode (High Risk)")

        # Check 2: User (Root check)
        # Config.User can be empty (defaulting to root) or "0" or "root"
        user = attrs.get('Config', {}).get('User', '')
        details['user'] = user
        if user == '' or user == '0' or user == 'root':
            score -= 30
            risks.append("Container is running as ROOT user (Medium Risk)")

        # Check 3: Exposed Ports (Heuristic)
        # Looking for mapping to sensitive host ports (e.g., < 1024, or specifically 22, 2375)
        ports = attrs.get('NetworkSettings', {}).get('Ports', {})
        details['ports'] = ports
        sensitive_ports = ['22/tcp', '2375/tcp', '2376/tcp']
        has_sensitive_port = False
        if ports:
            for container_port, host_bindings in ports.items():
                if container_port in sensitive_ports:
                    has_sensitive_port = True
                    break
        
        if has_sensitive_port:
            score -= 20
            risks.append("Container exposes sensitive ports (SSH/Docker socket) (Medium Risk)")

        # Check 4: Restart Policy (DoS risk if always restarting quickly)
        restart_policy = attrs.get('HostConfig', {}).get('RestartPolicy', {}).get('Name', '')
        details['restart_policy'] = restart_policy
        if restart_policy == 'always':
            # Minor penalty, can mask boot loops
            score -= 5
            risks.append("Restart policy is 'always' (Low Risk)")

        return {
            "score": max(0, score),
            "risks": risks,
            "details": details
        }
