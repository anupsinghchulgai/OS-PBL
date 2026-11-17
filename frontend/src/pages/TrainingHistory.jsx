import { useEffect, useState } from "react";
import { Eye, RefreshCw } from "lucide-react";
import PageHeader from "../components/common/PageHeader";
import Modal from "../components/common/Modal";
import { history } from "../services/mlService";
import { apiError } from "../services/api";
import { LoadingState, ErrorState, EmptyState } from "../components/common/States";

export default function TrainingHistory(){
 const [rows,setRows]=useState([]);const [loading,setLoading]=useState(true);const [error,setError]=useState("");const [detail,setDetail]=useState(null);
 const load=async()=>{setLoading(true);setError("");try{const r=await history();setRows(Array.isArray(r)?r:r?.history||r?.training_history||[])}catch(e){setError(apiError(e))}finally{setLoading(false)}};useEffect(()=>{load()},[]);
 return <><PageHeader title="Training History" description="Historical Random Forest training sessions returned from the backend database." actions={<button className="btn-secondary" onClick={load}><RefreshCw size={16}/>Refresh</button>}/>{error&&<ErrorState message={error} onRetry={load}/>}
 {loading?<LoadingState/>:rows.length?<div className="panel overflow-auto p-5"><table className="w-full text-left text-sm"><thead className="text-xs uppercase text-slate-500"><tr>{["Training ID","Dataset","Version","Model","Date","Workloads","Accuracy","F1","Status",""].map(x=><th key={x} className="px-3 py-2">{x}</th>)}</tr></thead><tbody className="divide-y divide-slate-800">{rows.map((r,i)=><tr key={r.training_id||r.id||i}><td className="px-3 py-3">{r.training_id||r.id||"—"}</td><td className="px-3 py-3">{r.dataset_name||r.dataset||"—"}</td><td className="px-3 py-3">{r.dataset_version||r.version||"—"}</td><td className="px-3 py-3">{r.model_version||"—"}</td><td className="px-3 py-3">{r.training_date||r.created_at||"—"}</td><td className="px-3 py-3">{r.workloads??r.workload_count??"—"}</td><td className="px-3 py-3">{r.accuracy??"—"}</td><td className="px-3 py-3">{r.f1_score??r.f1??"—"}</td><td className="px-3 py-3"><span className="rounded-full bg-slate-800 px-2 py-1 text-xs">{r.status||"—"}</span></td><td className="px-3 py-3"><button className="text-cyan-300" onClick={()=>setDetail(r)}><Eye size={16}/></button></td></tr>)}</tbody></table></div>:<EmptyState title="No training sessions" text="Completed and attempted model-training records will appear here when the backend exposes them."/>}
 <Modal open={!!detail} onClose={()=>setDetail(null)} title="Training Details" width="max-w-3xl"><pre className="max-h-[65vh] overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-400">{JSON.stringify(detail,null,2)}</pre></Modal>
 </>;
}
