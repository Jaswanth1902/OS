import pytest
from unittest.mock import MagicMock
from src.governance import GovernanceEngine

def test_governance_quarantine():
    controller = MagicMock()
    gov = GovernanceEngine(controller)
    
    # Secure container, high load -> No Action
    action = gov.evaluate("container1", cpu_usage=600000, security_score=100, risks=[])
    assert action is False
    controller.set_cpu_max.assert_not_called()

    # Insecure container, low load -> No Action
    action = gov.evaluate("container2", cpu_usage=10000, security_score=40, risks=["Privileged"])
    assert action is False
    controller.set_cpu_max.assert_not_called()

    # Insecure container, HIGH load -> Quarantine
    action = gov.evaluate("container3", cpu_usage=600000, security_score=40, risks=["Privileged"])
    assert action is True
    # Should set low CPU limit
    controller.set_cpu_max.assert_called_with("container3", 10000)
    
    # Check healing
    # Now container3 becomes secure
    action = gov.evaluate("container3", cpu_usage=600000, security_score=80, risks=[])
    assert action is True
    # Should set limit to None (unlimited)
    controller.set_cpu_max.assert_called_with("container3", None)
