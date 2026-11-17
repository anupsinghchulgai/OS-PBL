import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from "recharts";

const palette = ["#22d3ee","#8b5cf6","#60a5fa","#34d399","#f59e0b","#f472b6"];

export function ComparisonBarChart({ data, dataKey = "avg_waiting_time", label = "Average Waiting Time" }) {
  return <div className="h-72 w-full"><ResponsiveContainer><BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#1e293b"/><XAxis dataKey="algorithm" tick={{fill:"#94a3b8",fontSize:12}}/><YAxis tick={{fill:"#64748b",fontSize:12}}/><Tooltip contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:12}}/><Bar dataKey={dataKey} name={label} fill="#22d3ee" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div>;
}
export function ProbabilityChart({ data }) {
  return <div className="h-80 w-full"><ResponsiveContainer><PieChart><Pie data={data} dataKey="probability" nameKey="algorithm" cx="50%" cy="50%" outerRadius={105} label={({algorithm, probability}) => `${algorithm} ${Math.round(probability*100)}%`}>{data.map((_, i)=><Cell key={i} fill={palette[i % palette.length]}/>)}</Pie><Tooltip contentStyle={{background:"#0f172a",border:"1px solid #334155",borderRadius:12}}/></PieChart></ResponsiveContainer></div>;
}
