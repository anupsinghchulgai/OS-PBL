import pandas as pd
import numpy as np

ALGORITHMS = ["FCFS","SJF","SRTF","Round Robin","Preemptive Priority","Non-preemptive Priority"]

def workload_features(processes):
    df=pd.DataFrame(processes)
    if df.empty:
        return np.array([[0,0,0,0,0,0,0,0,0]], dtype=float)
    bt=df["burst_time"].astype(float)
    at=df["arrival_time"].astype(float)
    pr=df["priority"].astype(float)
    return np.array([[
        len(df), bt.mean(), bt.std(ddof=0), bt.max(), bt.min(),
        at.max(), at.mean(), pr.mean(), pr.std(ddof=0)
    ]], dtype=float)

FEATURE_NAMES=["process_count","burst_mean","burst_std","burst_max","burst_min","arrival_max","arrival_mean","priority_mean","priority_std"]
