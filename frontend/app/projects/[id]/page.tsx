"use client";

import React, { useState } from 'react';
import { Share2, FileText, CheckCircle2, AlertTriangle, PhoneCall, ExternalLink, Info, UserCircle2, Clock, ScrollText, MapPin } from 'lucide-react';

const DICT = {
  EN: {
    title: 'Project Details: Gomti Nagar Infrastructure Expansion',
    share: 'Share',
    verified: 'Verified Permit',
    status: 'ACTIVE',
    progress: 'Work Progress',
    auth: 'Issuing Authority',
    contractor: 'Lead Contractor',
    startDate: 'Start Date',
    endDate: 'Expected End',
    docs: 'Official Documents',
    docPreview: 'View NOC PDF',
    citizenReports: 'Citizen Reports',
    grievanceTitle: 'Grievance Redressal',
    cmHelpline: 'CM Helpline 1076',
    jansunwai: 'Jansunwai Portal',
    rtiRef: 'RTI Reference',
    rtiTooltip: 'Right to Information Act 2005 empowers citizens to seek verifiable information concerning government projects.',
    district: 'Lucknow Division'
  },
  HI: {
    title: 'प्रोजेक्ट विवरण: गोमती नगर इन्फ्रास्ट्रक्चर विस्तार',
    share: 'शेयर',
    verified: 'सत्यापित परमिट',
    status: 'सक्रिय',
    progress: 'कार्य प्रगति',
    auth: 'जारीकर्ता प्राधिकरण',
    contractor: 'मुख्य ठेकेदार',
    startDate: 'शुरुआत की तारीख',
    endDate: 'समाप्ति अनुमान',
    docs: 'आधिकारिक दस्तावेज़',
    docPreview: 'NOC पीडीएफ देखें',
    citizenReports: 'नागरिक रिपोर्ट',
    grievanceTitle: 'शिकायत निवारण',
    cmHelpline: 'सीएम हेल्पलाइन 1076',
    jansunwai: 'जनसुनवाई पोर्टल',
    rtiRef: 'आरटीआई संदर्भ',
    rtiTooltip: 'सूचना का अधिकार अधिनियम 2005 नागरिकों को सरकारी परियोजनाओं के संबंध में जानकारी मांगने का अधिकार देता है।',
    district: 'लखनऊ मंडल'
  }
};

const LOGO_MAP: Record<string, string> = {
    'LDA': '/logos/lda.svg',
    'LMC': '/logos/lmc.svg',
    'NHAI': '/logos/nhai.svg',
    'PWD_UP': '/logos/pwd.svg'
};

export default function ProjectDetail({ params }: { params: Promise<{ id: string }> }) {
    // Handling React use() hook for NextJS 15+ dynamic params safely
    const resolvedParams = React.use(params);
    const projectId = resolvedParams.id;

    const [lang, setLang] = useState<"EN" | "HI">("EN");
    const [tooltipOpen, setTooltipOpen] = useState(false);
    
    const t = DICT[lang];

    // Mock Payload for UP Authority
    const project = {
        id: projectId,
        authority: 'LDA',
        contractor: 'Larsen & Toubro Ltd. (UP Branch)',
        completionPercent: 68,
        reports: 3,
        rti: 'RTI/UP/2026/045'
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 font-sans p-6 pb-20">
            {/* Nav Component */}
            <div className="max-w-4xl mx-auto flex justify-between items-center mb-8">
                <button 
                  onClick={() => setLang(lang === 'EN' ? 'HI' : 'EN')} 
                  className="px-4 py-2 bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-700 rounded-xl font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                >
                    {lang === 'EN' ? 'हिंदी' : 'EN'}
                </button>
            </div>

            <main className="max-w-4xl mx-auto space-y-6">
                
                {/* Header Card */}
                <div className="bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm border border-slate-200 dark:border-slate-700 relative overflow-hidden">
                    <div className="flex justify-between items-start">
                        <div>
                            <div className="flex items-center gap-3 mb-4">
                                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-400 font-bold uppercase tracking-widest text-[11px] rounded-full">
                                    <CheckCircle2 size={14}/> {t.verified}
                                </span>
                                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-400 font-bold uppercase tracking-widest text-[11px] rounded-full">
                                    {t.status}
                                </span>
                            </div>
                            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white mb-3 leading-tight font-noto-deva">
                                {t.title}
                            </h1>
                            <p className="text-sm text-slate-500 dark:text-slate-400 font-bold flex flex-wrap items-center gap-4 uppercase tracking-wider">
                                <span>ID: {project.id}</span>
                                <span className="hidden sm:inline">•</span>
                                <span className="flex items-center gap-1"><MapPin size={16}/> {t.district}</span>
                            </p>
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-xl font-bold transition-colors">
                            <Share2 size={18}/> <span className="hidden sm:inline">{t.share}</span>
                        </button>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-700/50">
                        <div className="flex justify-between items-end mb-3">
                            <h3 className="text-sm font-black text-slate-800 dark:text-slate-300 uppercase tracking-widest">{t.progress}</h3>
                            <span className="text-3xl font-black text-blue-600 dark:text-blue-400">{project.completionPercent}%</span>
                        </div>
                        <div className="w-full h-5 bg-slate-100 dark:bg-slate-700/80 rounded-full overflow-hidden shadow-inner">
                            <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-1000" style={{ width: `${project.completionPercent}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* Grid Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Authority & Contractor */}
                    <div className="bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col gap-8">
                        <div className="flex items-center gap-5">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={LOGO_MAP[project.authority]} alt={project.authority} className="w-20 h-20 rounded-2xl object-contain bg-slate-50 p-2 border border-slate-100 dark:border-slate-700 shadow-sm"/>
                            <div>
                                <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1.5">{t.auth}</p>
                                <p className="font-black text-xl text-slate-800 dark:text-white flex items-center gap-2">
                                    {project.authority} <CheckCircle2 size={18} className="text-blue-500"/>
                                </p>
                            </div>
                        </div>
                        <div className="h-px w-full bg-slate-100 dark:bg-slate-700"></div>
                        <div className="flex items-center gap-5">
                            <div className="w-16 h-16 rounded-2xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400">
                                <UserCircle2 size={32}/>
                            </div>
                            <div>
                                <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1.5">{t.contractor}</p>
                                <p className="font-bold text-lg text-slate-800 dark:text-white leading-tight">{project.contractor}</p>
                            </div>
                        </div>
                    </div>

                    {/* Timeline & Reports */}
                    <div className="bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm border border-slate-200 dark:border-slate-700 flex flex-col gap-8">
                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">{t.startDate}</p>
                                <p className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2 text-lg"><Clock size={16} className="text-blue-500"/> Jan 2026</p>
                            </div>
                            <div>
                                <p className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2">{t.endDate}</p>
                                <p className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2 text-lg"><Clock size={16} className="text-indigo-500"/> Nov 2026</p>
                            </div>
                        </div>
                        <div className="h-px w-full bg-slate-100 dark:bg-slate-700"></div>
                        <div className="flex justify-between items-center p-6 bg-rose-50 dark:bg-rose-900/10 rounded-2xl border border-rose-100 dark:border-rose-900/30">
                            <div>
                                <p className="text-[11px] font-black text-rose-500 uppercase tracking-widest mb-1">{t.citizenReports}</p>
                                <p className="font-black text-3xl text-rose-600 dark:text-rose-400">{project.reports}</p>
                            </div>
                            <AlertTriangle size={36} className="text-rose-200 dark:text-rose-800/50"/>
                        </div>
                    </div>
                </div>

                {/* Permit Documents Viewer Mock */}
                <div className="bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm border border-slate-200 dark:border-slate-700">
                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <ScrollText size={18}/> {t.docs}
                    </h3>
                    <div className="w-full h-56 bg-slate-50 dark:bg-slate-700/30 rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-600 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700/60 transition-colors">
                        <FileText size={48} className="text-slate-300 dark:text-slate-600 mb-3"/>
                        <p className="font-bold text-slate-600 dark:text-slate-300 text-lg">{t.docPreview}</p>
                        <p className="text-sm font-semibold text-slate-400 mt-1 uppercase tracking-widest">PDF • 2.4 MB</p>
                    </div>
                </div>

                {/* Grievance Redressal UI Requirements */}
                <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl p-8 shadow-2xl border border-slate-700 text-white relative flex flex-col gap-6">
                    <h3 className="text-xs font-black uppercase tracking-widest flex items-center gap-2 text-slate-300">
                        <AlertTriangle size={18} className="text-amber-400"/> {t.grievanceTitle}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* CM Helpline */}
                        <a href="tel:1076" className="flex items-center gap-4 bg-white/5 hover:bg-white/10 p-5 rounded-2xl transition-colors border border-white/5 group">
                            <div className="bg-amber-500 group-hover:bg-amber-400 transition-colors p-3 rounded-xl text-white shadow-lg shadow-amber-500/20">
                                <PhoneCall size={20}/>
                            </div>
                            <span className="font-bold tracking-wide text-sm">{t.cmHelpline}</span>
                        </a>

                        {/* Jansunwai */}
                        <a href="https://jansunwai.up.nic.in" target="_blank" rel="noreferrer" className="flex items-center gap-4 bg-white/5 hover:bg-white/10 p-5 rounded-2xl transition-colors border border-white/5 group">
                            <div className="bg-blue-600 group-hover:bg-blue-500 transition-colors p-3 rounded-xl text-white shadow-lg shadow-blue-500/20">
                                <ExternalLink size={20}/>
                            </div>
                            <span className="font-bold tracking-wide text-sm">{t.jansunwai}</span>
                        </a>

                        {/* RTI Reference */}
                        {project.rti && (
                            <div className="relative flex items-center justify-between gap-4 bg-emerald-900/20 p-5 rounded-2xl border border-emerald-500/20">
                                <div>
                                    <p className="text-[10px] uppercase tracking-widest text-emerald-500/80 font-black mb-1.5">{t.rtiRef}</p>
                                    <p className="font-mono font-bold text-emerald-400 text-sm tracking-wide">{project.rti}</p>
                                </div>
                                <button 
                                  onMouseEnter={() => setTooltipOpen(true)} 
                                  onMouseLeave={() => setTooltipOpen(false)}
                                  className="text-emerald-500 hover:text-emerald-300 transition-colors p-2"
                                >
                                    <Info size={24}/>
                                </button>
                                
                                {tooltipOpen && (
                                    <div className="absolute top-0 right-0 transform translate-x-[15px] -translate-y-[calc(100%+15px)] bg-slate-100 text-slate-800 text-xs font-bold leading-relaxed p-4 rounded-xl shadow-2xl w-72 z-50 pointer-events-none border border-slate-200">
                                        {t.rtiTooltip}
                                        <div className="absolute bottom-0 right-7 transform translate-y-1/2 rotate-45 w-4 h-4 bg-slate-100 border-b border-r border-slate-200"></div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

            </main>
        </div>
    );
}
