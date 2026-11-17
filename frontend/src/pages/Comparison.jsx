import { useState } from "react";
import { GitCompare } from "lucide-react";
import PageHeader from "../components/common/PageHeader";
import { ComparisonBarChart } from "../components/charts/MetricsCharts";
import { compare } from "../services/schedulerService";
import { apiError } from "../services/api";
import { useApp } from "../context/AppContext";

export default function Comparison(){
 const {processes}=useApp(); const [state,setState]=useState({loading:false,error:null,data:null});
 const run=async()=>{setState({loading:true,error:null,data:null});try{const payload={processes:processes.map(p=>({pid:p.pid,arrival_time:Number(p.arrivalTime),burst_time:Number(p.burstTime),priority:Number(p.priority)})),algorithms:["FCFS","SJF","SRTF","Round Robin","Preemptive Priority","Non-preemptive Priority"]};setState({loading:false,error:null,data:await compare(payload)});}catch(e){setState({loading:false,error:apiError(e),data:null})}};
 const data=state.data?.comparison||state.data?.results||state.data; const rows=Array.isArray(data)?data: data?.algorithms||[];
 return <><PageHeader title="Algorithm Comparison" description="Run the same workload through all six algorithms using the backend comparison endpoint." actions={<button className="btn-primary" onClick={run} disabled={state.loading}><GitCompare size={16}/>{state.loading?"Comparing…":"Compare Algorithms"}</button>}/>{state.error&&<div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">{state.error}</div>}
 {rows.length?<><div className="panel mb-4 p-5"><h2 className="mb-4 font-bold">Average Waiting Time</h2><ComparisonBarChart data={rows.map(x=>({...x,algorithm:x.algorithm||x.name}))} dataKey="average_waiting_time"/></div><div className="panel overflow-auto p-5"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-slate-500"><tr>{Object.keys(rows[0]).map(k=><th className="px-3 py-2" key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody className="divide-y divide-slate-800">{rows.map((r,i)=><tr key={i}>{Object.values(r).map((v,j)=><td className="px-3 py-2" key={j}>{typeof v==="number"?Number(v.toFixed(3)):String(v)}</td>)}</tr>)}</tbody></table></div></>:<div className="panel flex min-h-96 items-center justify-center text-center p-8"><div><GitCompare className="mx-auto mb-3 text-slate-700" size={40}/><h2 className="font-bold">No comparison result</h2><p className="mt-1 text-sm text-slate-500">Run the backend comparison against the current workload.</p></div></div>}</>;
}
