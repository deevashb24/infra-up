"use client";

import React, { useState } from 'react';
import { CheckCircle2, ShieldAlert, PlusCircle, Building2 } from 'lucide-react';

const UP_AUTHORITIES = [
    'LDA', 
    'LMC', 
    'NHAI', 
    'PWD_UP', 
    'UPLCL', 
    'Jal Nigam', 
    'UPSIDA', 
    'Smart City Lucknow'
];

export default function AddProjectForm() {
    // FIX #5: Use env var so this works beyond localhost.
    const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [authority, setAuthority] = useState(UP_AUTHORITIES[0]);
    const [title, setTitle] = useState("");
    const [rawType, setRawType] = useState("सड़क निर्माण");
    
    // Hardcoded Lucknow coordinates for quick ingestion mocking
    const lng = 80.9462;
    const lat = 26.8467;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");
        
        try {
            const response = await fetch(`${API_BASE}/admin/ingest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    raw_type: rawType,
                    authority,
                    district: "Lucknow",
                    longitude: lng,
                    latitude: lat,
                    budget: 150.0
                })
            });
            if (response.ok) {
                setStatus("success");
                setTitle("");
                setTimeout(() => setStatus("idle"), 3000);
            } else {
                setStatus("error");
            }
        } catch {
            setStatus("error");
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center p-6 font-sans">
            <div className="w-full max-w-xl bg-white dark:bg-slate-800 rounded-3xl shadow-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                <div className="bg-blue-600 p-6 text-white flex items-center gap-4">
                    <Building2 size={32}/>
                    <div>
                        <h2 className="text-2xl font-black tracking-tight">Admin Portal</h2>
                        <p className="text-blue-200 text-sm font-medium">Ingest Infrastructure Project Node</p>
                    </div>
                </div>
                
                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Project Authority (Admin Bound to UP)</label>
                        <select 
                            value={authority}
                            onChange={(e) => setAuthority(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl outline-none border border-slate-200 dark:border-slate-600 font-semibold text-slate-800 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer"
                        >
                            {UP_AUTHORITIES.map(auth => (
                                <option key={auth} value={auth}>{auth}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Project Title</label>
                        <input 
                            required
                            type="text" 
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="e.g. Shaheed Path Flyover Expansion"
                            className="w-full bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl outline-none border border-slate-200 dark:border-slate-600 font-semibold text-slate-800 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-2">Raw Classification Native String</label>
                        <input 
                            required
                            type="text" 
                            value={rawType}
                            onChange={(e) => setRawType(e.target.value)}
                            placeholder="e.g. सड़क निर्माण or Utility Pipeline"
                            className="w-full bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl outline-none border border-slate-200 dark:border-slate-600 font-semibold text-slate-800 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all font-noto-deva"
                        />
                    </div>

                    <div className="pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between">
                        <div>
                            {status === 'loading' && <p className="text-blue-500 font-bold animate-pulse text-sm">Processing & Geocoding...</p>}
                            {status === 'success' && <p className="text-emerald-500 font-bold flex items-center gap-2 text-sm"><CheckCircle2 size={16}/> Project Ingested</p>}
                            {status === 'error' && <p className="text-rose-500 font-bold flex items-center gap-2 text-sm"><ShieldAlert size={16}/> Ingestion Failed</p>}
                        </div>
                        
                        <button 
                            type="submit" 
                            disabled={status === 'loading'}
                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl shadow-lg shadow-blue-500/30 font-black tracking-wide transition-all active:scale-95 disabled:opacity-50"
                        >
                            <PlusCircle size={20}/> Submit Record
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
