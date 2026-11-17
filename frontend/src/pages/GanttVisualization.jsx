import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import GanttChart from "../components/dashboard/GanttChart";
import { useApp } from "../context/AppContext";

export default function GanttVisualization(){
 const {latestSimulation}=useApp();
 return <><PageHeader title="Gantt Chart Visualization" description="Interactive rendering of the latest timeline returned by the scheduling backend." actions={<Link className="btn-secondary" to="/simulator">Run New Simulation</Link>}/>{latestSimulation?<><div className="mb-4 grid gap-3 sm:grid-cols-3">{[["Algorithm",latestSimulation.algorithm],["Segments",latestSimulation.timeline?.length],["Metric fields",Object.keys(latestSimulation.metrics||{}).length]].map(([a,b])=><div className="panel p-4" key={a}><p className="text-xs uppercase text-slate-500">{a}</p><p className="mt-1 font-bold">{b??"—"}</p></div>)}</div><GanttChart timeline={latestSimulation.timeline}/></>:<div className="panel p-10 text-center"><p className="text-slate-400">No latest simulation is stored. Run the CPU Simulator first.</p><Link className="btn-primary mt-4" to="/simulator">Open Simulator</Link></div>}</>;
}
