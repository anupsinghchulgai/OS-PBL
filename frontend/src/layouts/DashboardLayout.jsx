import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Activity, BarChart3, BrainCircuit, ChevronLeft, Database, Gauge, GitCompare, History, Info, LayoutDashboard, Menu, Moon, Settings, Sun, Table2, X } from "lucide-react";
import { useApp } from "../context/AppContext";

const groups = [
  { label:"MAIN", items:[
    ["/dashboard","Dashboard",LayoutDashboard],
    ["/processes","Process Management",Table2],
    ["/simulator","CPU Simulator",Gauge],
    ["/comparison","Algorithm Comparison",GitCompare],
    ["/gantt","Gantt Visualization",BarChart3]
  ]},
  { label:"MACHINE LEARNING", items:[
    ["/datasets","Dataset Management",Database],
    ["/training","Model Training",BrainCircuit],
    ["/recommendation","ML Recommendation",Activity],
    ["/history","Training History",History]
  ]},
  { label:"OTHER", items:[["/about","About Project",Info]]}
];

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobile, setMobile] = useState(false);
  const { theme, toggleTheme } = useApp();
  const location = useLocation();
  const current = groups.flatMap(g=>g.items).find(x=>location.pathname.startsWith(x[0]));
  return <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,_rgba(34,211,238,.07),_transparent_32%),#06101f]">
    <aside className={`fixed inset-y-0 left-0 z-40 hidden border-r border-slate-800 bg-slate-950/95 backdrop-blur md:block ${collapsed?"w-[78px]":"w-64"} transition-all`}>
      <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-400 text-slate-950 font-black">CS</div>
        {!collapsed && <div className="min-w-0"><p className="truncate text-sm font-bold">CPU Scheduling</p><p className="text-[10px] text-slate-500">Visualizer</p></div>}
      </div>
      <nav className="p-3">
        {groups.map(g=><div key={g.label} className="mb-5"><p className={`mb-2 px-2 text-[10px] font-bold tracking-[.18em] text-slate-600 ${collapsed?"text-center":""}`}>{collapsed?"•":g.label}</p>{g.items.map(([to,label,Icon])=><NavLink key={to} to={to} title={collapsed?label:undefined} className={({isActive})=>`mb-1 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive?"bg-cyan-400/10 text-cyan-300":"text-slate-400 hover:bg-slate-800/70 hover:text-slate-100"} ${collapsed?"justify-center":""}`}><Icon size={18}/>{!collapsed&&<span>{label}</span>}</NavLink>)}</div>)}
      </nav>
      <button onClick={()=>setCollapsed(!collapsed)} className="absolute bottom-5 right-[-13px] hidden h-7 w-7 items-center justify-center rounded-full border border-slate-700 bg-slate-900 text-slate-400 md:flex">{collapsed?<ChevronLeft size={15}/>:<ChevronLeft className="rotate-180" size={15}/>}</button>
    </aside>

    {mobile && <div className="fixed inset-0 z-50 bg-black/70 md:hidden" onClick={()=>setMobile(false)}><aside className="h-full w-72 bg-slate-950 p-4" onClick={e=>e.stopPropagation()}><div className="mb-5 flex justify-between"><div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400 text-slate-950 font-black">CS</div><b>CPU Scheduling</b></div><button onClick={()=>setMobile(false)}><X/></button></div>{groups.flatMap(g=>g.items).map(([to,label,Icon])=><NavLink onClick={()=>setMobile(false)} key={to} to={to} className="mb-1 flex gap-3 rounded-xl px-3 py-3 text-slate-300 hover:bg-slate-800"><Icon size={18}/>{label}</NavLink>)}</aside></div>}

    <main className={`${collapsed?"md:pl-[78px]":"md:pl-64"} min-h-screen transition-all`}>
      <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-800/80 bg-slate-950/75 px-4 backdrop-blur md:px-6">
        <div className="flex items-center gap-3"><button className="md:hidden" onClick={()=>setMobile(true)}><Menu/></button><div className="hidden text-xs text-slate-500 sm:block">Workspace / <span className="text-slate-300">{current?.[1] || "Dashboard"}</span></div></div>
        <div className="flex items-center gap-2"><button className="rounded-xl border border-slate-800 p-2 text-slate-400 hover:text-white" title="Settings"><Settings size={17}/></button><button onClick={toggleTheme} className="rounded-xl border border-slate-800 p-2 text-slate-400 hover:text-white">{theme==="dark"?<Sun size={17}/>:<Moon size={17}/>}</button><div className="ml-1 flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 text-xs font-black text-slate-950">OS</div></div>
      </header>
      <div className="mx-auto max-w-[1600px] p-4 md:p-6 lg:p-8"><Outlet/></div>
    </main>
  </div>;
}
