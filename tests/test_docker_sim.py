import sys
import os
import time
import threading

# Add src to path
sys.path.append(os.getcwd())

from src.dashboard_app import sim_engine

def test_simulation_lifecycle():
    print(">>> Starting Simulation Engine")
    sim_engine.start()
    
    print(">>> Sleeping 15s to allow Docker build/run and Agent start...")
    time.sleep(15)
    
    print(">>> Checking if 'os-ml-project' container exists...")
    ret = os.system("docker ps | findstr os-ml-project")
    if ret == 0:
        print("PASS: Docker container is running")
    else:
        print("FAIL: Docker container NOT found")
        
    print(">>> Stopping Simulation Engine")
    sim_engine.stop()
    
    time.sleep(5)
    print(">>> Checking if 'os-ml-project' is gone...")
    ret = os.system("docker ps | findstr os-ml-project")
    if ret != 0:
        print("PASS: Docker container successfully removed")
    else:
        print("FAIL: Docker container still exists")

if __name__ == "__main__":
    test_simulation_lifecycle()
