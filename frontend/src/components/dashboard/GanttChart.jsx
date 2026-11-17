import { useMemo } from "react";

const colors = ["#22d3ee","#8b5cf6","#60a5fa","#34d399","#f59e0b","#f472b6","#fb7185","#a3e635"];

export default function GanttChart({ timeline = [] }) {
  const max = useMemo(() => Math.max(...timeline.map(x => Number(x.end ?? x.end_time ?? x.finish ?? 0)), 0), [timeline]);
  if (!timeline.length) return <div className="panel p-8 text-center text-slate-500">No execution timeline is available yet.</div>;
  const min = Math.min(...timeline.map(x => Number(x.start ?? x.start_time ?? 0)));
  const range = Math.max(max - min, 1);
  return <div className="panel overflow-x-auto p-5">
    <div className="min-w-[760px]">
      <div className="mb-3 flex justify-between text-xs text-slate-500"><span>t={min}</span><span>t={max}</span></div>
      <div className="relative h-20 rounded-xl bg-slate-950/80">
        {timeline.map((seg, i) => {
          const start = Number(seg.start ?? seg.start_time ?? 0);
          const end = Number(seg.end ?? seg.end_time ?? seg.finish ?? start);
          const label = seg.pid ?? seg.process_id ?? seg.process ?? seg.name ?? (seg.id === "idle" ? "Idle" : "—");
          const left = ((start-min)/range)*100;
          const width = Math.max(((end-start)/range)*100, 0.7);
          const idle = String(label).toLowerCase() === "idle";
          return <div key={i} title={`${label}: ${start} → ${end}`} className={`absolute top-2 h-16 overflow-hidden rounded-lg border ${idle ? "border-slate-700 bg-slate-800" : "border-white/10"}`} style={{left:`${left}%`,width:`${width}%`,background: idle ? undefined : colors[i % colors.length]}}>
            <div className="flex h-full flex-col justify-center px-2 text-xs font-bold text-slate-950">{width > 4 ? label : ""}<span className="font-normal opacity-80">{width > 7 ? `${start}–${end}` : ""}</span></div>
          </div>
        })}
      </div>
      <div className="mt-3 flex justify-between text-[11px] text-slate-500"><span>{min}</span><span>{Math.round(min+range*.25)}</span><span>{Math.round(min+range*.5)}</span><span>{Math.round(min+range*.75)}</span><span>{max}</span></div>
    </div>
  </div>;
}
