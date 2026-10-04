import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  Target,
  CheckCircle2,
  ArrowRightCircle,
  AlertOctagon,
  Calendar,
  Sparkles,
  ChevronRight,
  BookOpen
} from 'lucide-react';

export default function SkillGaps() {
  const { matchResult, candidateProfile, jobData, setActiveTab } = useApp();
  const [gapData, setGapData] = useState(matchResult?.gap_analysis || null);
  const [loadingGaps, setLoadingGaps] = useState(false);

  useEffect(() => {
    if (matchResult?.gap_analysis) {
      setGapData(matchResult.gap_analysis);
    } else if (candidateProfile && jobData && !gapData) {
      async function fetchGaps() {
        setLoadingGaps(true);
        try {
          const res = await api.getSkillGaps(candidateProfile, jobData);
          setGapData(res);
        } catch (err) {
          console.error('Failed to compute skill gaps:', err);
        } finally {
          setLoadingGaps(false);
        }
      }
      fetchGaps();
    }
  }, [matchResult, candidateProfile, jobData]);

  if (!candidateProfile || !jobData) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400">
          <Target className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">Skill Gap Analysis Unavailable</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Please select or analyze a candidate resume and target job requisition to calculate ontology-based gaps and generate an upskilling roadmap.
          </p>
        </div>
        <button
          onClick={() => setActiveTab('workspace')}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md glow-indigo transition-all"
        >
          Open AI Match Workspace
        </button>
      </div>
    );
  }

  if (loadingGaps) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs font-mono text-slate-400">Calculating ontology skill gaps &amp; generating 4-week roadmap...</p>
      </div>
    );
  }

  const {
    coverage_ratio = 0,
    matched_required_skills = 0,
    total_required_skills = 0,
    strong_skills = [],
    transferable_skills = [],
    missing_skills = [],
    upskilling_roadmap = []
  } = gapData || {};

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Ontology Skill Gap &amp; Upskilling Roadmap
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {coverage_ratio}% Coverage
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Identifies verified strengths, adjacent transferable competencies with transfer credits, and targeted 4-week bridging milestones.
        </p>
      </div>

      {/* Coverage Ratio Card */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-1">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
            Required Qualification Coverage
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{coverage_ratio}%</span>
            <span className="text-xs text-slate-400">
              ({matched_required_skills} of {total_required_skills} required qualifications directly verified or transferred)
            </span>
          </div>
          <div className="w-full sm:w-80 bg-slate-800 rounded-full h-2 mt-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, coverage_ratio)}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="text-center p-3 rounded-xl bg-[#0B0F19]">
            <div className="text-slate-500">STRONG</div>
            <div className="text-lg font-bold text-emerald-400">{strong_skills.length}</div>
          </div>
          <div className="text-center p-3 rounded-xl bg-[#0B0F19]">
            <div className="text-slate-500">TRANSFERABLE</div>
            <div className="text-lg font-bold text-cyan-400">{transferable_skills.length}</div>
          </div>
          <div className="text-center p-3 rounded-xl bg-[#0B0F19]">
            <div className="text-slate-500">MISSING</div>
            <div className="text-lg font-bold text-rose-400">{missing_skills.length}</div>
          </div>
        </div>
      </div>

      {/* 3-Column Categorization Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Strong Skills */}
        <div className="glass-card rounded-2xl p-5 border border-emerald-500/20 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            <span>Verified Strengths ({strong_skills.length})</span>
          </div>
          <p className="text-xs text-slate-400">
            Qualifications with direct evidence in candidate experience or projects.
          </p>
          <div className="space-y-2 pt-1">
            {strong_skills.map((s, idx) => (
              <div key={idx} className="p-2.5 rounded-xl bg-[#0B0F19]/80 border border-white/5 text-xs">
                <div className="font-semibold text-white">{s.skill_name}</div>
                {s.explanation && (
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{s.explanation}</p>
                )}
              </div>
            ))}
            {strong_skills.length === 0 && (
              <p className="text-xs text-slate-500 italic">No direct matches identified.</p>
            )}
          </div>
        </div>

        {/* Transferable Skills */}
        <div className="glass-card rounded-2xl p-5 border border-cyan-500/20 space-y-3">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold uppercase tracking-wider">
            <ArrowRightCircle className="w-4 h-4" />
            <span>Transferable Bridges ({transferable_skills.length})</span>
          </div>
          <p className="text-xs text-slate-400">
            Adjacent technologies where prior knowledge accelerates ramp-up.
          </p>
          <div className="space-y-2 pt-1">
            {transferable_skills.map((s, idx) => (
              <div key={idx} className="p-2.5 rounded-xl bg-[#0B0F19]/80 border border-white/5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{s.skill_name}</span>
                  <span className="text-[10px] font-mono text-cyan-400 px-1.5 py-0.5 rounded bg-cyan-500/10">
                    via {s.matched_candidate_skill}
                  </span>
                </div>
                {s.explanation && (
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{s.explanation}</p>
                )}
              </div>
            ))}
            {transferable_skills.length === 0 && (
              <p className="text-xs text-slate-500 italic">No transferable bridges identified.</p>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div className="glass-card rounded-2xl p-5 border border-rose-500/20 space-y-3">
          <div className="flex items-center gap-2 text-rose-400 text-xs font-mono font-bold uppercase tracking-wider">
            <AlertOctagon className="w-4 h-4" />
            <span>Missing Gaps ({missing_skills.length})</span>
          </div>
          <p className="text-xs text-slate-400">
            Target requirements with zero identified supporting evidence.
          </p>
          <div className="space-y-2 pt-1">
            {missing_skills.map((s, idx) => (
              <div key={idx} className="p-2.5 rounded-xl bg-[#0B0F19]/80 border border-white/5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{s.skill_name}</span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                    s.priority_level === 'HIGH'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : 'bg-amber-500/10 text-amber-400'
                  }`}>
                    {s.priority_level || 'MEDIUM'}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  {s.is_required ? 'Mandatory Qualification' : 'Preferred Qualification'}
                </div>
              </div>
            ))}
            {missing_skills.length === 0 && (
              <p className="text-xs text-slate-500 italic">No missing requirements found!</p>
            )}
          </div>
        </div>
      </div>

      {/* 4-Week Milestone Upskilling Roadmap */}
      {upskilling_roadmap?.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white">
              Targeted 4-Week Milestone Upskilling Roadmap
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {upskilling_roadmap.map((milestone, idx) => (
              <div key={idx} className="glass-card rounded-2xl p-5 border border-white/5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 font-mono text-xs flex items-center justify-center font-bold">
                      {milestone.week || idx + 1}
                    </span>
                    <span className="text-xs font-mono font-bold text-indigo-300 uppercase tracking-wider">
                      {milestone.phase}
                    </span>
                  </div>
                </div>

                {/* Focus Skills */}
                <div className="flex flex-wrap gap-1.5">
                  {milestone.focus_skills?.map((sk, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[11px] font-mono">
                      {sk}
                    </span>
                  ))}
                </div>

                {/* Action Items */}
                <ul className="space-y-1.5 pt-1">
                  {milestone.action_items?.map((act, aIdx) => (
                    <li key={aIdx} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                      <ChevronRight className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

