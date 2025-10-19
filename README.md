# 📦 Virtual Automated Warehouse Simulator

A SimPy-based virtual automated warehouse simulation system with multiple scheduling strategies and inventory management capabilities.

## 🚀 Quick Start

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install simpy streamlit pandas numpy matplotlib
```

### Run Simulation
```bash
# Basic simulation test
python sim_core.py

# Launch Streamlit dashboard
streamlit run app.py

# Run experiment analysis
python experiments.py
```

## 🏗️ System Architecture

### Core Components

1. **Order Class**: Order entity containing arrival time, processing time, priority, product type, etc.
2. **WarehouseSim Class**: Warehouse simulation core, managing resources, queues, inventory and scheduling strategies
3. **KPIs Class**: Key performance indicators collector
4. **Scheduling Strategies**: FIFO, SPT, EDD, PRIORITY

### Features

- ✅ **Multi-strategy Scheduling**: Supports first-come-first-served, shortest processing time, earliest due date, priority scheduling
- ✅ **Inventory Management**: Real-time inventory tracking, automatic replenishment, stockout handling
- ✅ **Performance Monitoring**: Wait time, flow time, throughput, WIP peak and other KPIs
- ✅ **Visualization Interface**: Streamlit interactive dashboard
- ✅ **Experiment Analysis**: A/B testing, load sensitivity analysis, capacity planning

## 📊 Key Performance Indicators (KPIs)

| Metric | Description |
|--------|-------------|
| `avg_wait` | Average wait time |
| `p90_wait` | 90th percentile wait time |
| `avg_flow` | Average flow time |
| `throughput_per_hr` | Throughput per hour |
| `wip_peak` | Work-in-process peak |
| `stockout_rate` | Stockout rate |
| `replenishments` | Number of replenishments |

## 🎯 Scheduling Strategies

### FIFO (First In, First Out)
- First-come-first-served, sorted by arrival time
- Simple and fair, suitable for low-load scenarios

### SPT (Shortest Processing Time)
- Shortest processing time first, same processing time sorted by arrival time
- Reduces average wait time, but may cause long task starvation

### EDD (Earliest Due Date)
- Earliest due date first, same due date sorted by arrival time
- Suitable for scenarios with clear deadlines

### PRIORITY
- Priority scheduling, high priority orders processed first
- **Supports aging factor**: Low priority orders waiting for a long time gradually increase priority
- Prevents starvation phenomenon, improves system fairness

## 🧪 Experiment Analysis

### A/B Testing
Compare performance of different scheduling strategies under the same conditions:
```python
python experiments.py
```

### Load Sensitivity Analysis
Analyze system performance changes under different loads:
- Change arrival rate (λ)
- Observe wait time vs utilization curve

### Capacity Planning
Determine optimal number of servers:
- Test 1-10 AGVs/workstations
- Find diminishing returns point

## 📁 Project Structure

```
VIRTUAL_WAREHOUSE/
├── sim_core.py          # Simulation core
├── app.py              # Streamlit application
├── experiments.py      # Experiment scripts
├── README.md           # Project documentation
├── venv/               # Virtual environment
└── experiments/        # Experiment results
    ├── ab_test_results.csv
    ├── load_sensitivity_results.csv
    └── capacity_planning_results.csv
```

## 🔧 Configuration Parameters

### Simulation Parameters
- `sim_time`: Simulation time (seconds)
- `num_servers`: Number of AGVs/workstations
- `lam`: Mean inter-arrival time (seconds)
- `mean_proc`: Mean processing time (seconds)

### Inventory Parameters
- `initial_inventory`: Initial inventory
- `reorder_point`: Reorder point
- `reorder_quantity`: Reorder quantity

## 📈 Usage Examples

### Basic Simulation
```python
from sim_core import run_once

# Run single simulation
result = run_once(
    sim_time=3600,
    num_servers=2,
    policy='FIFO',
    lam=10,
    mean_proc=8
)
print(result)
```

### Strategy Comparison
```python
policies = ['FIFO', 'SPT', 'EDD', 'PRIORITY']
results = []

for policy in policies:
    result = run_once(policy=policy, sim_time=1800)
    results.append(result)

# Compare results
import pandas as pd
df = pd.DataFrame(results)
print(df[['policy', 'avg_wait', 'throughput_per_hr']])
```

## 🎨 Visualization Interface

After launching the Streamlit application, you can:

1. **Adjust Parameters**: Modify simulation parameters in the sidebar
2. **Select Strategies**: Choose scheduling strategies to compare
3. **View Results**: View KPI tables and charts in real-time
4. **Download Data**: Export results data in CSV format

## 🔬 Advanced Features

### Inventory Management
- 10 product types
- Random order quantities (1-5 items)
- Automatic replenishment mechanism
- Stockout waiting queue

### Experiment Design
- Multiple runs to ensure statistical significance
- Confidence interval calculation
- Result visualization export

## 📝 Resume Highlights

**Built a discrete-event virtual warehouse with inventory backorders and replenishment delays in SimPy, benchmarked dispatching rules (FIFO/SPT/EDD/Priority+aging), and added stockout-aware KPIs. Implemented a Streamlit dashboard and a reproducible batch-experiment harness; improved P90 wait time under high utilization via aging-augmented priority scheduling.**

**Implemented KPI analytics (lead time, WIP peak, throughput, stockout rate) and automated experiment runner with CSV exports for reproducible studies.**

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

## 📄 License

MIT License
