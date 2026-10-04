import React from 'react';
import { useApp } from '../context/AppContext';
import {
  LayoutDashboard,
  FileText,
  Layers,
  Target,
  Wand2,
  Sparkles,
  Network,
  Binary,
  BarChart3,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export default function Sidebar() {
  const { activeTab, setActiveTab, candidateProfile, jobData, matchResult } = useApp();

  const navSections = [
    {
      title: 'CORE APPLICATION PIPELINE',
      items: [
        {
          id: 'overview',
          label: 'Executive Overview',
          icon: LayoutDashboard,
          badge: null,
        },
        {
          id: 'workspace',
          label: 'AI Match Workspace',
          icon: FileText,
          badge: candidateProfile ? 'Active' : null,
          badgeColor: 'text-emerald-400 bg-emerald-500/10',
        },
        {
          id: 'match',
          label: 'Match Breakdown',
          icon: Layers,
          badge: matchResult ? `${matchResult.overall_score}%` : null,
          badgeColor: 'text-indigo-400 bg-indigo-500/10',
        },
        {
          id: 'gaps',
          label: 'Skill Gap & Roadmap',
          icon: Target,
          badge: null,
        },
        {
          id: 'improve',
          label: 'Resume Improver',
          icon: Wand2,
          badge: null,
        },
        {
          id: 'recommendations',
          label: 'Role Recommendations',
          icon: Sparkles,
          badge: null,
        },
      ],
    },
    {
      title: 'ENGINEERING DEEP DIVES',
      items: [
        {
          id: 'architecture',
          label: 'System Architecture',
          icon: Network,
          badge: 'Design',
          badgeColor: 'text-cyan-400 bg-cyan-500/10',
        },
        {
          id: 'ontology',
          label: 'Skill Ontology (36 Skills)',
          icon: Binary,
          badge: 'Taxonomy',
          badgeColor: 'text-purple-400 bg-purple-500/10',
        },
        {
          id: 'evaluation',
          label: 'Quality Benchmarks',
          icon: BarChart3,
          badge: 'F1: 0.929',
          badgeColor: 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20',
        },
      ],
    },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-[#0B0F19]/95 border-r border-white/10 flex flex-col justify-between h-[calc(100vh-61px)] sticky top-[61px] overflow-y-auto">
      <div className="p-4 space-y-6">
        {navSections.map((section, idx) => (
          <div key={idx}>
            <h3 className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold px-3 mb-2">
              {section.title}
            </h3>
            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-indigo-600/20 text-white border border-indigo-500/30 shadow-sm glow-indigo'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Profile State Indicator */}
      <div className="p-4 border-t border-white/5 bg-[#070B13]/60">
        <div className="text-[11px] font-mono text-slate-400 space-y-1.5">
          <div className="flex items-center justify-between">
            <span>Resume Status:</span>
            <span className={candidateProfile ? 'text-emerald-400 flex items-center gap-1 font-sans' : 'text-slate-500'}>
              {candidateProfile ? <CheckCircle className="w-3 h-3 inline" /> : null}
              {candidateProfile ? 'Loaded' : 'Empty'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span>Target Requisition:</span>
            <span className={jobData ? 'text-emerald-400 flex items-center gap-1 font-sans' : 'text-slate-500'}>
              {jobData ? <CheckCircle className="w-3 h-3 inline" /> : null}
              {jobData ? 'Selected' : 'Empty'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

