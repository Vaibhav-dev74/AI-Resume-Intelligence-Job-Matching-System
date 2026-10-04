import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  Wand2,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  TrendingUp,
  Sparkles,
  FileCheck
} from 'lucide-react';

export default function ResumeImprovement() {
  const { candidateProfile, candidateRawText, improvementResult, setImprovementResult, setActiveTab } = useApp();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (candidateProfile && !improvementResult) {
      async function runImprovement() {
        setLoading(true);
        try {
          const res = await api.improveResume(candidateProfile, candidateRawText);
          setImprovementResult(res);
        } catch (err) {
          console.error('Failed to run resume improver:', err);
        } finally {
          setLoading(false);
        }
      }
      runImprovement();
    }
  }, [candidateProfile, improvementResult]);

  if (!candidateProfile) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
          <Wand2 className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">No Candidate Resume Loaded</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Please upload or choose a candidate resume from the workspace to generate evidence-constrained bullet improvements.
          </p>
        </div>
        <button
          onClick={() => setActiveTab('workspace')}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md glow-indigo transition-all"
        >
          Go to AI Match Workspace
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs font-mono text-slate-400">Auditing resume action verbs and calculating strength score...</p>
      </div>
    );
  }

  const {
    strength_score = 65,
    overall_critique = '',
    suggestions = [],
    formatting_insights = []
  } = improvementResult || {};

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Evidence-Constrained Resume Improver
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Zero Hallucination
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Analyzes candidate achievements, replaces passive weak verbs with high-impact engineering leadership verbs, and highlights opportunities for quantifiable outcomes.
        </p>
      </div>

      {/* Top Cards: Score & Overall Critique */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Strength Score Card */}
        <div className="glass-card rounded-2xl p-6 border border-white/5 flex flex-col items-center justify-center text-center">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">
            Resume Strength Index
          </span>
          <div className="flex items-baseline gap-1 my-1">
            <span className="text-5xl font-extrabold text-white font-mono">{strength_score}</span>
            <span className="text-lg text-slate-500">/100</span>
          </div>
          <div className="w-48 bg-slate-800 rounded-full h-2 my-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, strength_score)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            {suggestions.length} high-impact improvements identified
          </p>
        </div>

        {/* Executive Critique */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-white/5 space-y-3 flex flex-col justify-center">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
            <TrendingUp className="w-4 h-4" />
            <span>EXECUTIVE DIAGNOSTIC CRITIQUE</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed">
            {overall_critique || 'Resume structure meets standard formatting requirements. Applying the action-oriented revisions below will strengthen engineering signals.'}
          </p>
          {formatting_insights?.length > 0 && (
            <div className="pt-2 border-t border-white/5 space-y-1">
              {formatting_insights.map((insight, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-slate-400">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>{insight}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Suggested Bullet Revisions */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Targeted Bullet Enhancements</span>
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            {suggestions.length} suggestions
          </span>
        </div>

        <div className="space-y-4">
          {suggestions.map((item, idx) => (
            <div key={idx} className="glass-card rounded-2xl p-5 border border-white/5 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-mono text-indigo-400 font-semibold">
                  {item.section || 'Experience Section'}
                </span>
                {item.weak_verb && (
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-rose-500/10 text-rose-300 border border-rose-500/20">
                    Weak Verb: "{item.weak_verb}"
                  </span>
                )}
              </div>

              {/* Original Bullet */}
              <div className="p-3 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">
                  ORIGINAL CANDIDATE TEXT:
                </span>
                <p className="text-xs text-slate-300 italic">
                  "{item.original_bullet}"
                </p>
              </div>

              {/* Improved Bullet Suggestion */}
              <div className="p-3.5 rounded-xl bg-gradient-to-r from-indigo-950/40 to-slate-900 border border-indigo-500/30 space-y-2 glow-indigo">
                <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider font-semibold block flex items-center gap-1.5">
                  <FileCheck className="w-3.5 h-3.5" />
                  <span>ACTION-ORIENTED REVISED BULLET:</span>
                </span>
                <p className="text-xs text-white font-medium leading-relaxed">
                  "{item.improved_bullet}"
                </p>
              </div>

              {/* Action Alternatives Pills */}
              {item.action_verb_alternatives?.length > 0 && (
                <div className="flex items-center gap-2 text-xs pt-1">
                  <span className="text-slate-500 font-mono text-[11px]">Recommended Verbs:</span>
                  <div className="flex flex-wrap gap-1">
                    {item.action_verb_alternatives.map((alt, aIdx) => (
                      <span key={aIdx} className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[10px] font-mono">
                        {alt}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {suggestions.length === 0 && (
            <div className="p-8 text-center glass-card rounded-2xl border border-white/5 text-slate-400 text-xs">
              All parsed bullet points demonstrate strong action verbs and quantified engineering outcomes.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

