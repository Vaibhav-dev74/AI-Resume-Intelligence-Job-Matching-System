import React from 'react';
import { useApp } from '../context/AppContext';
import { Cpu, Activity, User, Briefcase, Sparkles, ChevronRight } from 'lucide-react';

export default function Navbar() {
  const {
    systemHealth,
    candidateProfile,
    jobData,
    activeTab,
    setActiveTab,
    selectPresetResume,
    selectPresetJob,
    presets,
    executeMatch,
    loading,
  } = useApp();

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/10 px-4 lg:px-8 py-3 transition-all">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-[1px] flex items-center justify-center glow-indigo shadow-lg">
            <div className="w-full h-full bg-[#0B0F19] rounded-[11px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white">
                IntelliResume <span className="text-indigo-400">AI</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400 font-normal hidden sm:block">
              Explainable Resume Intelligence & Dense Job Requisition Matching
            </p>
          </div>
        </div>

        {/* Center: Active Profile & Job Indicators */}
        <div className="hidden md:flex items-center gap-2 bg-[#0B0F19]/90 border border-white/10 rounded-xl px-3 py-1.5 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <User className="w-3.5 h-3.5 text-indigo-400" />
            <span className="max-w-[130px] truncate font-medium">
              {candidateProfile?.full_name || 'No Candidate Loaded'}
            </span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <div className="flex items-center gap-1.5 text-slate-300">
            <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
            <span className="max-w-[140px] truncate font-medium">
              {jobData?.title || 'No Job Selected'}
            </span>
          </div>
        </div>

        {/* Right: Health Status & Demo Preset Quick Actions */}
        <div className="flex items-center gap-3">
          {/* Health Pill */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900/80 border border-white/10 text-xs">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${systemHealth ? 'bg-emerald-400' : 'bg-rose-400'}`} />
              <span className={`relative inline-flex rounded-full h-2 w-2 ${systemHealth ? 'bg-emerald-500' : 'bg-rose-500'}`} />
            </span>
            <span className="text-[11px] font-mono text-slate-300 hidden lg:inline">
              {systemHealth ? 'FastAPI Online (MiniLM-L6-v2)' : 'Connecting Backend...'}
            </span>
          </div>

          {/* Quick Demo Button */}
          {!candidateProfile && (
            <button
              onClick={() => {
                selectPresetResume('Alice Chen (Senior ML Engineer)');
                selectPresetJob('Apex Robotics - Senior Machine Learning Engineer');
                setActiveTab('workspace');
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-xs font-semibold shadow-md transition-all"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Load Demo Data</span>
            </button>
          )}

          {candidateProfile && jobData && (
            <button
              onClick={() => executeMatch()}
              disabled={loading}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md glow-emerald transition-all disabled:opacity-50"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>{loading ? 'Matching...' : 'Run Match'}</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

