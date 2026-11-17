import { X } from "lucide-react";
export default function Modal({ open, title, onClose, children, width = "max-w-lg" }) {
  if (!open) return null;
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onMouseDown={e => e.target === e.currentTarget && onClose()}>
    <div className={`w-full ${width} panel max-h-[90vh] overflow-auto p-5`}>
      <div className="mb-5 flex items-center justify-between"><h2 className="text-lg font-bold">{title}</h2><button className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white" onClick={onClose}><X size={18}/></button></div>
      {children}
    </div>
  </div>;
}
