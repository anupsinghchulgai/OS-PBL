from copy import deepcopy
from typing import List, Dict, Any
import math

ALGORITHMS = [
    "FCFS", "SJF", "SRTF", "Round Robin",
    "Preemptive Priority", "Non-preemptive Priority"
]

def _p(p):
    return {
        "pid": str(p["pid"]),
        "arrival_time": float(p["arrival_time"]),
        "burst_time": float(p["burst_time"]),
        "priority": float(p.get("priority", 1)),
        "remaining": float(p["burst_time"]),
    }

def _metrics(processes, timeline):
    by_pid = {p["pid"]: p for p in processes}
    starts, finishes = {}, {}
    context_switches = 0
    last_pid = None
    busy = 0.0
    for s in timeline:
        pid = s["pid"]
        start, end = float(s["start"]), float(s["end"])
        if end <= start: continue
        if pid != "IDLE":
            busy += end - start
            starts[pid] = min(starts.get(pid, start), start)
            finishes[pid] = max(finishes.get(pid, end), end)
            if last_pid is not None and last_pid != pid:
                context_switches += 1
            last_pid = pid
    rows = []
    waits, turns, responses = [], [], []
    for p in processes:
        pid = p["pid"]
        completion = finishes.get(pid, p["arrival_time"] + p["burst_time"])
        turnaround = completion - p["arrival_time"]
        waiting = max(turnaround - p["burst_time"], 0)
        response = max(starts.get(pid, p["arrival_time"]) - p["arrival_time"], 0)
        waits.append(waiting); turns.append(turnaround); responses.append(response)
        rows.append({
            "pid": pid, "arrival_time": p["arrival_time"], "burst_time": p["burst_time"],
            "priority": p["priority"], "completion_time": completion,
            "turnaround_time": turnaround, "waiting_time": waiting, "response_time": response
        })
    total_time = (max((x["end"] for x in timeline), default=0) -
                  min((x["start"] for x in timeline), default=0))
    util = (busy / total_time * 100) if total_time else 0
    return {
        "average_waiting_time": sum(waits)/len(waits) if waits else 0,
        "average_turnaround_time": sum(turns)/len(turns) if turns else 0,
        "average_response_time": sum(responses)/len(responses) if responses else 0,
        "cpu_utilization": util,
        "throughput": len(processes)/total_time if total_time else 0,
        "context_switches": context_switches,
        "processes": rows
    }

def _append(timeline, pid, start, end):
    if end <= start: return
    if timeline and timeline[-1]["pid"] == pid and abs(timeline[-1]["end"] - start) < 1e-9:
        timeline[-1]["end"] = end
    else:
        timeline.append({"pid": pid, "start": start, "end": end})

def fcfs(ps):
    t=0; tl=[]
    for p in sorted(ps, key=lambda x:(x["arrival_time"], x["pid"])):
        if t < p["arrival_time"]:
            _append(tl,"IDLE",t,p["arrival_time"]); t=p["arrival_time"]
        _append(tl,p["pid"],t,t+p["burst_time"]); t+=p["burst_time"]
    return tl

def sjf(ps, preemptive=False):
    t=0; tl=[]; remaining=deepcopy(ps); finished=set()
    while len(finished)<len(ps):
        available=[p for p in remaining if p["pid"] not in finished and p["arrival_time"]<=t+1e-9 and p["remaining"]>1e-9]
        if not available:
            next_t=min(p["arrival_time"] for p in remaining if p["pid"] not in finished and p["remaining"]>1e-9)
            _append(tl,"IDLE",t,next_t); t=next_t; continue
        if preemptive:
            chosen=min(available,key=lambda x:(x["remaining"],x["arrival_time"],x["pid"]))
            next_arrivals=[p["arrival_time"] for p in remaining if p["pid"] not in finished and p["arrival_time"]>t+1e-9]
            next_t=min(next_arrivals) if next_arrivals else math.inf
            run=min(chosen["remaining"], next_t-t)
        else:
            chosen=min(available,key=lambda x:(x["burst_time"],x["arrival_time"],x["pid"]))
            run=chosen["remaining"]
        _append(tl,chosen["pid"],t,t+run); chosen["remaining"]-=run; t+=run
        if chosen["remaining"]<=1e-9: finished.add(chosen["pid"])
    return tl

def priority(ps, preemptive=False):
    t=0; tl=[]; rem=deepcopy(ps); finished=set()
    while len(finished)<len(ps):
        avail=[p for p in rem if p["pid"] not in finished and p["arrival_time"]<=t+1e-9 and p["remaining"]>1e-9]
        if not avail:
            nxt=min(p["arrival_time"] for p in rem if p["pid"] not in finished and p["remaining"]>1e-9)
            _append(tl,"IDLE",t,nxt); t=nxt; continue
        chosen=min(avail,key=lambda x:(x["priority"],x["arrival_time"],x["pid"]))
        if preemptive:
            arrivals=sorted(p["arrival_time"] for p in rem if p["pid"] not in finished and p["arrival_time"]>t+1e-9)
            run=min(chosen["remaining"], (arrivals[0]-t) if arrivals else chosen["remaining"])
        else: run=chosen["remaining"]
        _append(tl,chosen["pid"],t,t+run); chosen["remaining"]-=run; t+=run
        if chosen["remaining"]<=1e-9: finished.add(chosen["pid"])
    return tl

def round_robin(ps, q):
    rem=deepcopy(ps); tl=[]; t=0; queue=[]; arrived=set(); finished=set()
    def enqueue_until(time):
        for p in sorted(rem,key=lambda x:(x["arrival_time"],x["pid"])):
            if p["pid"] not in arrived and p["arrival_time"]<=time+1e-9:
                queue.append(p); arrived.add(p["pid"])
    while len(finished)<len(ps):
        enqueue_until(t)
        if not queue:
            nxt=min(p["arrival_time"] for p in rem if p["pid"] not in arrived)
            _append(tl,"IDLE",t,nxt); t=nxt; enqueue_until(t)
        p=queue.pop(0)
        run=min(q,p["remaining"])
        # If a new process arrives during the slice it is queued after the current process.
        _append(tl,p["pid"],t,t+run); t+=run; p["remaining"]-=run
        enqueue_until(t)
        if p["remaining"]>1e-9: queue.append(p)
        else: finished.add(p["pid"])
    return tl

def simulate(processes, algorithm, quantum=2):
    if algorithm not in ALGORITHMS: raise ValueError(f"Unsupported algorithm: {algorithm}")
    ps=[_p(x) for x in processes]
    if algorithm=="FCFS": tl=fcfs(ps)
    elif algorithm=="SJF": tl=sjf(ps,False)
    elif algorithm=="SRTF": tl=sjf(ps,True)
    elif algorithm=="Round Robin": tl=round_robin(ps,quantum)
    elif algorithm=="Preemptive Priority": tl=priority(ps,True)
    else: tl=priority(ps,False)
    return {"algorithm":algorithm,"timeline":tl,"metrics":_metrics(ps,tl)}

def compare(processes, algorithms=None, quantum=2):
    algorithms=algorithms or ALGORITHMS
    out=[]
    for alg in algorithms:
        result=simulate(processes,alg,quantum)
        out.append({"algorithm":alg, **{k:v for k,v in result["metrics"].items() if k!="processes"}})
    return {"results":out}
