import time
import math
import sys
import threading

def log(msg):
    print(f"[ML-WORKLOAD] {msg}", flush=True)

def cpu_stress(duration, intensity=1.0):
    t_end = time.time() + duration
    while time.time() < t_end:
        if intensity > 0:
            math.factorial(5000)
            time.sleep(1.0 - intensity if intensity < 1.0 else 0)

def memory_stress(duration, size_mb):
    data = []
    chunk_size = 10 * 1024 * 1024 # 10MB chunks
    target_chunks = int(size_mb / 10)
    
    for i in range(target_chunks):
        if time.time() > time.time() + duration: break
        data.append(bytearray(chunk_size))
        time.sleep(0.1) # Gradual ramp
        
    time.sleep(duration - (target_chunks * 0.1))

def run_phase(name, duration, cpu_int, mem_mb):
    log(f"Starting Phase: {name} ({duration}s)")
    t1 = threading.Thread(target=cpu_stress, args=(duration, cpu_int))
    t1.start()
    
    if mem_mb > 0:
        memory_stress(duration, mem_mb)
    
    t1.join()
    log(f"Completed Phase: {name}")

if __name__ == "__main__":
    log("Container Started. Initializing environment...")
    time.sleep(5)
    
    # 2 Minute Lifecycle
    start_time = time.time()
    
    # 0-10s: Init
    run_phase("Initialization", 10, 0.1, 50)
    
    # 10-40s: Data Loading
    run_phase("Data Loading", 30, 0.3, 1500) # Load 1.5GB
    
    # 40-100s: Training
    run_phase("Model Training", 60, 1.0, 2000) # Max CPU, 2GB Mem
    
    # 100-120s: Cool down
    run_phase("Completion", 20, 0.1, 100)
    
    log("Workload Complete. Sleeping...")
    while True:
        time.sleep(10)
