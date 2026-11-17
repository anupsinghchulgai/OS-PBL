import { CheckCircle2, XCircle } from "lucide-react";
export default function Toast({ toast, onClose }) {
  if (!toast) return null;
  return <div className="fixed bottom-5 right-5 z-[60] w-[min(420px,calc(100vw-2rem))] panel p-4 shadow-2xl">
    <div className="flex gap-3">{toast.type === "error" ? <XCircle className="text-red-400"/> : <CheckCircle2 className="text-emerald-400"/>}<div className="flex-1"><p className="font-semibold">{toast.title}</p><p className="mt-1 text-sm text-slate-400">{toast.message}</p></div><button onClick={onClose} className="text-slate-500">×</button></div>
  </div>;
}
