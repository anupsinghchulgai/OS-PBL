import { useEffect, useState } from "react";
import { Activity, Database, Gauge, ListChecks, BrainCircuit, Play, Upload, BarChart3 } from "lucide-react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import { LoadingState, ErrorState, EmptyState } from "../components/common/States";
import { apiError } from "../services/api";
import { health } from "../services/schedulerService";
import { listDatasets } from "../services/datasetService";
import { history } from "../services/mlService";
import { useApp } from "../context/AppContext";

export default function Dashboard() {
  const { processes, latestSimulation } = useApp();
  const [state,setState]=useState({loading:true,error:null,datasets:[],history:[],health:null});
  const load=async()=>{setState(s=>({...s,loading:true,error:null}));try{const [h,d,hist]=await Promise.allSettled([health(),listDatasets(),history()]);setState({loading:false,error:null,health:h.status==="fulfilled"?h.value:null,datasets:d.status==="fulfilled"?(Array.isArray(d.value)?d.value:d.value?.datasets||[]):[],history:hist.status==="fulfilled"?(Array.isArray(hist.value)?hist.value:hist.value?.history||[]):[]});}catch(e){setState(s=>({...s,loading:false,error:apiError(e)}));}};
  useEffect(()=>{load()},[]);
  const metrics=latestSimulation?.metrics||{};
  return <><PageHeader title="Dashboard" description="Operational overview of scheduling simulations, datasets and Random Forest model activity." actions={<><Link className="btn-primary" to="/simulator"><Play size={16}/>New Simulation</Link><Link className="btn-secondary" to="/datasets"><Upload size={16}/>Manage Dataset</Link></>}/>
    {state.error&&<ErrorState message={state.error} onRetry={load}/>}
    {state.loading?<LoadingState/>:<>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Processes" value={processes.length} hint="Current workload" icon={ListChecks}/>
        <StatCard label="Total Datasets" value={state.datasets.length} hint="Backend datasets" icon={Database}/>
        <StatCard label="Total Simulations" value={latestSimulation?"1+":"0"} hint="Current browser session" icon={Gauge}/>
        <StatCard label="ML Model" value={state.history[0]?.status||"Not trained"} hint={state.health?"Backend healthy":"Backend status unavailable"} icon={BrainCircuit}/>
      </div>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Avg Waiting Time" value={metrics.average_waiting_time ?? metrics.avg_waiting_time} icon={Activity}/>
        <StatCard label="Avg Turnaround" value={metrics.average_turnaround_time ?? metrics.avg_turnaround_time} icon={Activity}/>
        <StatCard label="CPU Utilization" value={metrics.cpu_utilization != null ? `${metrics.cpu_utilization}%` : undefined} icon={Gauge}/>
        <StatCard label="Backend" value={state.health?"Online":"Unknown"} hint="GET /health" icon={Activity}/>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="panel p-5"><div className="mb-4 flex items-center justify-between"><div><h2 className="font-bold">Recent Simulation</h2><p className="muted">Latest backend result retained for quick access.</p></div><Link to="/gantt" className="btn-secondary">Open Gantt</Link></div>{latestSimulation?<pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-400">{JSON.stringify(latestSimulation.metrics||latestSimulation,null,2)}</pre>:<EmptyState title="No simulation yet" text="Run a scheduling simulation to populate this section."/>}</div>
        <div className="panel p-5"><div className="mb-4 flex items-center justify-between"><div><h2 className="font-bold">ML Activity</h2><p className="muted">Training sessions returned by the backend.</p></div><Link to="/history" className="btn-secondary">View History</Link></div>{state.history.length?<div className="space-y-2">{state.history.slice(0,5).map((x,i)=><div key={x.training_id||x.id||i} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/40 p-3"><div><p className="text-sm font-semibold">{x.dataset_name||x.dataset||"Dataset"}</p><p className="text-xs text-slate-500">{x.model_version||"Model"} · {x.status||"Unknown"}</p></div><span className="text-xs text-slate-400">{x.accuracy ?? "—"}</span></div>)}</div>:<EmptyState title="No training history" text="Train a Random Forest model using a managed dataset."/>}</div>
      </div>
    </>}
  </>;
}
