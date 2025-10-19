"""
Quick experiment script - Run a small number of experiments for demonstration
"""
import pandas as pd
import numpy as np
from sim_core import run_once

def quick_demo():
    """Quick demonstration of different strategy performance"""
    print("Virtual Warehouse Simulator - Quick Demo")
    print("=" * 50)
    
    policies = ['FIFO', 'SPT', 'EDD', 'PRIORITY']
    results = []
    
    for i, policy in enumerate(policies):
        print(f"Running {policy}...")
        result = run_once(policy=policy, sim_time=1800, seed=42, seed_offset=i)
        results.append(result)
    
    df = pd.DataFrame(results)
    
    print("\nResults Summary:")
    print(df[['policy', 'completed', 'avg_wait', 'throughput_per_hr', 'stockout_rate']].to_string(index=False))
    
    # 找出最佳策略
    best_wait = df.loc[df['avg_wait'].idxmin(), 'policy']
    best_throughput = df.loc[df['throughput_per_hr'].idxmax(), 'policy']
    
    print(f"\nBest Strategy for Wait Time: {best_wait}")
    print(f"Best Strategy for Throughput: {best_throughput}")
    
    return df

if __name__ == "__main__":
    quick_demo()
