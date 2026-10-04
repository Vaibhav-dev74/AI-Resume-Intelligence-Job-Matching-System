import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  Sparkles,
  Briefcase,
  CheckCircle2,
  ArrowRightCircle,
  AlertOctagon,
  ArrowRight,
  TrendingUp
} from 'lucide-react';

export default function JobRecommendations() {
  const { candidateProfile, recommendations, setRecommendations, setJobData, setJobRawText, presets, setActiveTab, executeMatch } = useApp();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (candidateProfile && !recommendations) {
      async function fetchRecs() {
        setLoading(true);
        try {
          const recList = await api.getRecommendations(candidateProfile);
          setRecommendations(recList);
        } catch (err) {
          console.error('Failed to get job recommendations:', err);
        } finally {
          setLoading(false);
        }
      }
      fetchRecs();
    }
  }, [candidateProfile, recommendations]);

  if (!candidateProfile) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
          <Sparkles className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">Recommendations Unavailable</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Please upload or choose a candidate resume to rank job requisitions based on dense embedding cosine similarity and ontology skill overlap.
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
        <p className="text-xs font-mono text-slate-400">Encoding candidate dense vectors and ranking available requisitions...</p>
      </div>
    );
  }

  const handleSelectJob = (rec) => {
    // Find preset job matching title
    const foundPresetKey = Object.keys(presets.jobs || {}).find((key) => key.includes(rec.title) || rec.title.includes(key));
    if (foundPresetKey) {
      const p = presets.jobs[foundPresetKey];
      setJobData(p.job_data);
      setJobRawText(p.raw_text);
    } else {
      setJobData({
        title: rec.title,
        company: rec.company,
        required_skills: rec.matched_skills.concat(rec.missing_skills),
        preferred_skills: rec.transferable_skills,
      });
    }
    setActiveTab('workspace');
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Role Recommendations &amp; Job Ranking
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Dense Cosine Ranking
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Candidate: <span className="text-white font-semibold">{candidateProfile.full_name}</span> • Ranks open requisitions using dense 384-dimensional text vectors and skill graph alignment.
        </p>
      </div>

      {/* Recommendations Cards */}
      <div className="space-y-4">
        {recommendations?.map((rec, idx) => (
          <div
            key={idx}
            className="glass-card rounded-2xl p-6 border border-white/5 space-y-4 hover:border-indigo-500/30 transition-all"
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono text-sm flex items-center justify-center font-bold">
                  #{rec.rank || idx + 1}
                </span>
                <div>
                  <h3 className="text-lg font-bold text-white">
                    {rec.title}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {rec.company}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs font-mono text-slate-400">COMPATIBILITY FIT</div>
                  <div className="text-2xl font-extrabold text-emerald-400 font-mono">
                    {rec.overall_fit_score || rec.fit_score}%
                  </div>
                </div>

                <button
                  onClick={() => handleSelectJob(rec)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md glow-indigo transition-all"
                >
                  <span>Select &amp; Analyze</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Rationale */}
            {rec.match_rationale && (
              <p className="text-xs text-slate-300 leading-relaxed font-sans bg-[#0B0F19]/60 p-3 rounded-xl border border-white/5">
                {rec.match_rationale}
              </p>
            )}

            {/* Skills Tags Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-1">
              <div>
                <span className="text-[11px] font-mono text-emerald-400 font-semibold uppercase tracking-wider block mb-1.5">
                  ✓ Matched Qualifications ({rec.matched_skills?.length || 0})
                </span>
                <div className="flex flex-wrap gap-1">
                  {rec.matched_skills?.map((s, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono">
                      {s}
                    </span>
                  ))}
                  {(!rec.matched_skills || rec.matched_skills.length === 0) && (
                    <span className="text-slate-500 text-[10px]">None</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[11px] font-mono text-cyan-400 font-semibold uppercase tracking-wider block mb-1.5">
                  ↔ Transferable Adjacent ({rec.transferable_skills?.length || 0})
                </span>
                <div className="flex flex-wrap gap-1">
                  {rec.transferable_skills?.map((s, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-[10px] font-mono">
                      {s}
                    </span>
                  ))}
                  {(!rec.transferable_skills || rec.transferable_skills.length === 0) && (
                    <span className="text-slate-500 text-[10px]">None</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[11px] font-mono text-rose-400 font-semibold uppercase tracking-wider block mb-1.5">
                  ✗ Target Skill Gaps ({rec.missing_skills?.length || 0})
                </span>
                <div className="flex flex-wrap gap-1">
                  {rec.missing_skills?.map((s, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[10px] font-mono">
                      {s}
                    </span>
                  ))}
                  {(!rec.missing_skills || rec.missing_skills.length === 0) && (
                    <span className="text-slate-500 text-[10px]">No gaps</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {(!recommendations || recommendations.length === 0) && !loading && (
          <div className="p-8 text-center glass-card rounded-2xl border border-white/5 text-slate-400 text-xs">
            No recommendations generated.
          </div>
        )}
      </div>
    </div>
  );
}

