export default function StatCard({ label, value, hint, icon: Icon }) {
  return <div className="panel p-5"><div className="flex items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold text-white">{value ?? "—"}</p>{hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}</div>{Icon && <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 p-2.5 text-cyan-300"><Icon size={20}/></div>}</div></div>;
}
