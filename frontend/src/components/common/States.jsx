import { AlertTriangle, LoaderCircle, Inbox } from "lucide-react";

export function LoadingState({ text = "Loading…" }) {
  return <div className="flex min-h-32 items-center justify-center gap-2 text-slate-400"><LoaderCircle className="animate-spin" size={18}/>{text}</div>;
}
export function ErrorState({ message, onRetry }) {
  return <div className="panel border-red-500/20 p-5"><div className="flex items-start gap-3"><AlertTriangle className="mt-0.5 text-red-400" size={20}/><div><p className="font-semibold text-red-300">Something went wrong</p><p className="mt-1 text-sm text-slate-400">{message}</p>{onRetry && <button className="btn-secondary mt-4" onClick={onRetry}>Retry</button>}</div></div></div>;
}
export function EmptyState({ title, text }) {
  return <div className="panel flex min-h-40 flex-col items-center justify-center p-6 text-center"><Inbox className="mb-3 text-slate-600" size={28}/><h3 className="font-semibold">{title}</h3><p className="mt-1 max-w-md text-sm text-slate-500">{text}</p></div>;
}
