import streamlit as st
import pandas as pd
import numpy as np
from sim_core import run_once

st.set_page_config(page_title="Virtual Warehouse Simulator", layout="wide")

st.title("📦 Virtual Automated Warehouse — Policy Benchmark")

with st.sidebar:
    st.header("Simulation Settings")
    sim_time = st.slider("Simulation time (seconds)", 600, 7200, 3600, 300)
    num_servers = st.slider("Number of AGVs/Stations", 1, 10, 2, 1)
    lam = st.slider("Mean inter-arrival (sec)", 2, 60, 10, 1)
    mean_proc = st.slider("Mean processing time (sec)", 2, 60, 8, 1)
    seed = st.number_input("Random seed", 0, 9999, 42)
    
    st.header("Inventory Settings")
    initial_inventory = st.slider("Initial inventory per item", 10, 200, 100, 10)
    reorder_point = st.slider("Reorder point", 5, 50, 20, 5)
    reorder_quantity = st.slider("Reorder quantity", 10, 100, 50, 10)

    st.header("Policies to Compare")
    policies = st.multiselect(
        "Select policies",
        ["FIFO", "SPT", "EDD", "PRIORITY"],
        default=["FIFO", "SPT", "PRIORITY"]
    )

run = st.button("Run Simulation")

if run:
    if not policies:
        st.warning("Please select at least one policy to run.")
        st.stop()
    
    try:
        with st.spinner("Running simulation..."):
            rows = []
            for i, p in enumerate(policies):
                rows.append(run_once(
                    sim_time=sim_time,
                    num_servers=num_servers,
                    policy=p,
                    lam=lam,
                    mean_proc=mean_proc,
                    seed=seed,
                    seed_offset=i,  # Different strategies use different seed offsets
                    initial_inventory=initial_inventory,
                    reorder_point=reorder_point,
                    reorder_quantity=reorder_quantity
                ))
    except Exception as e:
        st.error(f"Simulation failed: {e}")
        st.stop()
    df = pd.DataFrame(rows)
    st.subheader("KPI Summary")
    st.dataframe(df, use_container_width=True)

    st.subheader("Throughput per hour")
    st.bar_chart(df.set_index("policy")["throughput_per_hr"])

    st.subheader("Average Wait vs. 90th Percentile Wait")
    st.line_chart(df.set_index("policy")[["avg_wait", "p90_wait"]])

    st.subheader("Peak WIP")
    st.bar_chart(df.set_index("policy")["wip_peak"])
    
    st.subheader("Stockout Rate")
    st.bar_chart(df.set_index("policy")["stockout_rate"])
    
    st.subheader("Replenishments")
    st.bar_chart(df.set_index("policy")["replenishments"])

    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="warehouse_sim_results.csv",
        mime="text/csv"
    )
else:
    st.info("Select parameters on the left sidebar, then click **Run Simulation**.")
