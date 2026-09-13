<div align="center">

![OS Simulator Banner](assets/os_simulator_banner.svg)

# 🖥️ OS Simulator: Kernel Paging & Process Scheduling Suite
### *Comparative Systems Benchmarks, LRU/FIFO Page Replacement & Banker's Deadlock Avoidance*

[![Core: C / C++](https://img.shields.io/badge/Core-C_%7C_C++-00599C?style=flat-square&logo=c%2B%2B&logoColor=white)](https://github.com/Jaswanth1902/OS)
[![Scheduling: Round--Robin & SJF](https://img.shields.io/badge/Scheduling-Round--Robin_%7C_SJF-38BDF8?style=flat-square)](https://github.com/Jaswanth1902/OS)
[![Virtual Memory: LRU & FIFO](https://img.shields.io/badge/Memory-LRU_%7C_Optimal_Paging-10B981?style=flat-square)](https://github.com/Jaswanth1902/OS)
[![Deadlock: Banker's Algorithm](https://img.shields.io/badge/Safety-Banker's_Algorithm-F59E0B?style=flat-square)](https://github.com/Jaswanth1902/OS)
[![License: MIT](https://img.shields.io/badge/License-MIT-C5A059.svg?style=flat-square)](LICENSE)

*A comprehensive systems simulation workbench modeling operating system kernel mechanics, CPU scheduling efficiencies, and virtual memory page fault curves.*

</div>

---

## ⚡ The Architectural Vision

Understanding low-level operating system scheduling and memory management trade-offs requires empirical simulation rather than theoretical abstraction. 

**OS Simulator** delivers an interactive systems benchmark evaluating classic kernel algorithms under deterministic workloads:
- **CPU Scheduling Algorithms**: First-Come First-Served (FCFS), Shortest Job First (SJF), Round-Robin (RR) with dynamic quantum slicing, and Priority Preemptive scheduling.
- **Virtual Memory Page Replacement**: Least Recently Used (LRU), First-In First-Out (FIFO), and Optimal (OPT) page replacement algorithms comparing empirical page fault rates and Belady's Anomaly.
- **Deadlock Avoidance**: Banker's Algorithm safety and resource-request state machine verifying safe execution sequences.

---

## 🏗️ Kernel Simulation Architecture

```mermaid
flowchart TD
    Workload([Process Task Pool / Memory Reference String]) --> Engine{OS Kernel Simulator}
    
    subgraph CPUScheduler["1. CPU Scheduling Subsystem"]
        Engine --> FCFS["First-Come First-Served (FCFS)"]
        Engine --> SJF["Shortest Job First (SJF / SRTF)"]
        Engine --> RR["Round-Robin (Time Quantum q)"]
        FCFS & SJF & RR --> CPUMetrics["Turnaround & Waiting Time Analysis"]
    end

    subgraph VirtualMemory["2. Virtual Memory Management"]
        Engine --> FIFOPage["FIFO Page Replacement"]
        Engine --> LRUPage["LRU Page Replacement (Stack / Aging)"]
        Engine --> OPTPage["Optimal Page Replacement"]
        FIFOPage & LRUPage & OPTPage --> PageFaults["Page Fault Rate Analysis"]
    end

    subgraph DeadlockSafety["3. Concurrency & Deadlock Engine"]
        Engine --> Bankers["Banker's Safety Algorithm
(Available, Max, Allocation, Need Matrices)"]
        Bankers --> SafeSeq["Safe Sequence Resolution or Deadlock Detection"]
    end
```

---

## 🧩 Antigravity Skills & Tooling

- **`performance-profiling`**: Microsecond turnaround comparison across CPU scheduling algorithms.
- **`systematic-debugging`**: Edge-case testing of zero-quantum and circular-wait deadlock scenarios.
- **`clean-code`**: Strict decoupling of process descriptors (`PCB`) from queue traversal logic.

---

## 🚀 Quickstart

```bash
# Compile CPU scheduler suite
gcc -O2 -o scheduler cpu_scheduling.c
./scheduler

# Run memory paging benchmarks
gcc -O2 -o paging page_replacement.c
./paging
```

---

## 📄 License

Distributed under the [MIT License](LICENSE). Maintained by [Jaswanth Reddy](https://github.com/Jaswanth1902) — *Passionate learner & creative problem solver learning from and giving back to the open-source community.*
