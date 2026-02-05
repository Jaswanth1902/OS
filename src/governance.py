import logging
from typing import Dict, List, Optional

class GovernanceEngine:
    """
    Enforces policies based on container state (Resource Usage + Security Score).
    """

    def __init__(self, controller):
        self.controller = controller
        self.quarantined_containers = set()

    def evaluate(self, container_id: str, cpu_usage: int, security_score: int, risks: List[str]):
        """
        Evaluates strict policies.
        
        Policy 1: Quarantine High Risk & High Load
        If Security Score < 50 AND CPU > 90% (heuristic threshold):
            -> Clamp CPU to 1% (1000 usec per 100ms or similar small value)
        """
        # Heuristic: If score is low and CPU is high (e.g., > 1 core usage assuming 1000000 base)
        # Note: cpu_usage is in usec. 1 vCPU = 1,000,000 usec/sec roughly if normalized? 
        # Actually cpu.stat usage_usec is cumulative. We need RATE.
        # But for now, let's assume the input `cpu_usage` here is the PREDICTED rate or recent usage rate passed from agent.
        
        # In the agent, 'pred_cpu' is the predicted usage.
        
        if security_score < 50:
            # Check if it needs quarantine
            # We treat 'pred_cpu' > 500,000 (0.5 cores) as "High Load" for a "Vulnerable" container
            if cpu_usage > 500000:
                if container_id not in self.quarantined_containers:
                    logging.warning(f"SECURITY ALERT: Quarantining container {container_id} (Score: {security_score}, CPU: {cpu_usage})")
                    self.enforce_quarantine(container_id)
                return True # Action taken
        
        if container_id in self.quarantined_containers and security_score >= 50:
            # Heal
            logging.info(f"Container {container_id} security score improved ({security_score}). Releasing from quarantine.")
            self.release_quarantine(container_id)
            return True

        return False

    def enforce_quarantine(self, container_id: str):
        """Severely scales down the container resources."""
        # 10,000 usec = 10ms every 100ms = 0.1 CPU
        self.controller.set_cpu_max(container_id, 10000) 
        self.quarantined_containers.add(container_id)

    def release_quarantine(self, container_id: str):
        """Releases resource limits (sets to max)."""
        self.controller.set_cpu_max(container_id, None) # Unlimited
        self.quarantined_containers.remove(container_id)
