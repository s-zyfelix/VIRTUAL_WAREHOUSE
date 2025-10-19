"""
Experiment scripts: A/B testing, load sensitivity analysis, capacity planning
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sim_core import run_once
import os

def run_ab_test(policies=['FIFO', 'SPT', 'EDD', 'PRIORITY'], 
                num_runs=30, sim_time=3600, **kwargs):
    """A/B testing: Compare performance of different strategies"""
    results = []
    
    for policy in policies:
        print(f"Running {num_runs} simulations for {policy}...")
        for run in range(num_runs):
            result = run_once(policy=policy, sim_time=sim_time, seed=42, seed_offset=run, **kwargs)
            result['run'] = run
            results.append(result)
    
    return pd.DataFrame(results)

def load_sensitivity_analysis():
    """Load sensitivity analysis: Change arrival rate, observe wait time changes"""
    lam_values = np.linspace(5, 25, 10)  # Inter-arrival time from 5 to 25 seconds
    results = []
    
    for lam in lam_values:
        print(f"Testing arrival rate: {lam:.1f}")
        for run in range(10):  # Run 10 times for each point
            result = run_once(lam=lam, seed=42, seed_offset=run, sim_time=1800)
            result['lam'] = lam
            result['utilization'] = 8 / lam  # Assume processing time is 8 seconds
            results.append(result)
    
    return pd.DataFrame(results)

def capacity_planning():
    """Capacity planning: Change number of servers, find diminishing returns point"""
    server_counts = range(1, 11)
    results = []
    
    for num_servers in server_counts:
        print(f"Testing {num_servers} servers...")
        for run in range(10):
            result = run_once(num_servers=num_servers, seed=42, seed_offset=run, sim_time=1800)
            result['num_servers'] = num_servers
            results.append(result)
    
    return pd.DataFrame(results)

def plot_results(df, title, x_col, y_col, save_path=None):
    """Plot result charts"""
    plt.figure(figsize=(10, 6))
    
    if 'policy' in df.columns:
        # Group by policy
        for policy in df['policy'].unique():
            policy_data = df[df['policy'] == policy]
            mean_vals = policy_data.groupby(x_col)[y_col].mean()
            std_vals = policy_data.groupby(x_col)[y_col].std()
            
            plt.errorbar(mean_vals.index, mean_vals.values, 
                        yerr=std_vals.values, label=policy, marker='o')
    else:
        # Single strategy
        mean_vals = df.groupby(x_col)[y_col].mean()
        std_vals = df.groupby(x_col)[y_col].std()
        plt.errorbar(mean_vals.index, mean_vals.values, 
                    yerr=std_vals.values, marker='o')
    
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Run all experiments"""
    print("Starting Virtual Warehouse Experiments...")
    
    # Create results directory
    os.makedirs('experiments', exist_ok=True)
    
    # 1. A/B testing
    print("\nRunning A/B Test...")
    ab_results = run_ab_test()
    ab_results.to_csv('experiments/ab_test_results.csv', index=False)
    
    # Plot A/B test results
    plot_results(ab_results, 'Policy Comparison: Average Wait Time', 
                'policy', 'avg_wait', 'experiments/ab_test_wait.png')
    plot_results(ab_results, 'Policy Comparison: Throughput', 
                'policy', 'throughput_per_hr', 'experiments/ab_test_throughput.png')
    
    # 2. Load sensitivity analysis
    print("\nRunning Load Sensitivity Analysis...")
    load_results = load_sensitivity_analysis()
    load_results.to_csv('experiments/load_sensitivity_results.csv', index=False)
    
    plot_results(load_results, 'Load Sensitivity: Wait Time vs Utilization', 
                'utilization', 'avg_wait', 'experiments/load_sensitivity.png')
    
    # 3. Capacity planning
    print("\nRunning Capacity Planning Analysis...")
    capacity_results = capacity_planning()
    capacity_results.to_csv('experiments/capacity_planning_results.csv', index=False)
    
    plot_results(capacity_results, 'Capacity Planning: Throughput vs Servers', 
                'num_servers', 'throughput_per_hr', 'experiments/capacity_planning.png')
    
    print("\nAll experiments completed! Check the 'experiments' folder for results.")

if __name__ == "__main__":
    main()
