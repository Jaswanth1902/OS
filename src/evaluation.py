import csv
import time
import random
import logging

class EvaluationSuite:
    """
    Runs scenarios to compare OS-level resource control effectiveness.
    Generates 'evaluation_report.csv'.
    """

    def __init__(self, agent_controller):
        self.controller = agent_controller
        self.results = []

    def run_scenario(self, name: str, duration_sec: int, mode: str):
        """
        Runs a simulated workload under specific mode.
        mode: 'static' (fixed limit) or 'dynamic' (AI agent control)
        """
        logging.info(f"Starting Scenario: {name} ({mode})")
        start_time = time.time()
        
        # Simulated metrics accumulator
        total_cpu_allocated = 0
        total_cpu_used = 0
        oom_kills = 0
        throttled_events = 0

        for i in range(duration_sec):
            # Simulate Application Load (Random Walk)
            # Base load + spikes
            app_demand = 100000 + (random.random() * 50000) # Base 100k-150k
            if i % 10 == 0: # Spike every 10s
                app_demand += 200000 
            
            # Determine Limit based on mode
            if mode == 'static':
                limit = 200000 # Hard limit 0.2 CPU
            else:
                # Dynamic: Simulate Agent prediction (Perfect prediction for simplicity)
                limit = app_demand * 1.1 
            
            # Metrics
            used = min(app_demand, limit)
            waste = max(0, limit - used)
            
            if app_demand > limit:
                throttled_events += 1
                # In extreme cases, this could be OOM or Crash
                if (app_demand - limit) > 100000:
                    oom_kills += 1
            
            total_cpu_allocated += limit
            total_cpu_used += used
            
            time.sleep(0.1) # Accelerated simulation (1s loop = 0.1s real)

        # Calculate aggregations
        efficiency = (total_cpu_used / total_cpu_allocated) * 100 if total_cpu_allocated > 0 else 0
        
        report = {
            "Scenario": name,
            "Mode": mode,
            "Duration": duration_sec,
            "Total_Allocated": int(total_cpu_allocated),
            "Total_Used": int(total_cpu_used),
            "Waste": int(total_cpu_allocated - total_cpu_used),
            "Efficiency_Percent": round(efficiency, 2),
            "Throttled_Events": throttled_events,
            "OOM_Kills": oom_kills
        }
        self.results.append(report)
        return report

    def export_csv(self, filename="evaluation_report.csv"):
        if not self.results:
            return
        keys = self.results[0].keys()
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.results)
        logging.info(f"Report exported to {filename}")

if __name__ == "__main__":
    # Self-test
    logging.basicConfig(level=logging.INFO)
    evaluator = EvaluationSuite(None)
    evaluator.run_scenario("Web Server Load", 20, "static")
    evaluator.run_scenario("Web Server Load", 20, "dynamic")
    evaluator.export_csv()
