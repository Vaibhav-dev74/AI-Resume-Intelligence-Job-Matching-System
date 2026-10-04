import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import ScoreGauge from '../components/ScoreGauge';
import PolarRadarChart from '../components/PolarRadarChart';
import EvidenceCard from '../components/EvidenceCard';
import {
  Layers,
  FileText,
  Download,
  Copy,
  Check,
  Filter,
  CheckCircle2,
  ArrowRightCircle,
  Sparkles,
  XCircle,
  HelpCircle
} from 'lucide-react';

export default function MatchAnalysis() {
  const { matchResult, candidateProfile, jobData, setActiveTab, selectPresetResume, selectPresetJob } = useApp();
  const [filterType, setFilterType] = useState('all'); // 'all' | 'required' | 'preferred'
  const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'direct_match' | 'transferable_match' | 'inferred' | 'missing'
  const [copied, setCopied] = useState(false);

  if (!matchResult) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
          <Layers className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">No Active Match Analysis</h2>
          <p className="text-sm text-slate-400 max-w-md mx-auto">
            Load a candidate resume and job requisition from the workspace or choose a pre-evaluated benchmark pair.
          </p>
        </div>
        <div className="flex justify-center gap-3">
          <button
            onClick={() => setActiveTab('workspace')}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md glow-indigo transition-all"
          >
            Go to AI Match Workspace
          </button>
          <button
            onClick={() => {
              selectPresetResume('Alice Chen (Senior ML Engineer)');
              selectPresetJob('Apex Robotics - Senior Machine Learning Engineer');
              setActiveTab('workspace');
            }}
            className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs font-semibold transition-all"
          >
            Load Alice Chen Demo
          </button>
        </div>
      </div>
    );
  }

  const { overall_score, breakdown, evidences = [], synthesis_explanation, scoring_weights } = matchResult;

  // Filter evidence items
  const filteredEvidences = evidences.filter((ev) => {
    if (filterType === 'required' && !ev.is_required) return false;
    if (filterType === 'preferred' && ev.is_required) return false;
    if (statusFilter !== 'all' && ev.match_status !== statusFilter) return false;
    return true;
  });

  const directCount = evidences.filter((e) => e.match_status === 'direct_match').length;
  const transCount = evidences.filter((e) => e.match_status === 'transferable_match').length;
  const inferredCount = evidences.filter((e) => e.match_status === 'inferred').length;
  const missingCount = evidences.filter((e) => e.match_status === 'missing').length;

  const handleCopyReport = () => {
    const reportText = `# IntelliResume AI Match Report
Candidate: ${candidateProfile?.full_name || 'Candidate'}
Target Role: ${jobData?.title || 'Target Job'} (${jobData?.company || 'Company'})
Overall Compatibility: ${overall_score}%

## 8-Layer Factor Breakdown
${Object.entries(breakdown || {})
  .map(([k, v]) => `- ${v.label}: ${v.score}% (Weight: ${(v.weight * 100).toFixed(0)}%, Contribution: ${v.contribution}%)`)
  .join('\n')}

## Synthesis Evaluation
${synthesis_explanation}

## Verified Evidence Items (${evidences.length} total)
${evidences
  .map(
    (e) =>
      `### ${e.skill_name} [${e.is_required ? 'REQUIRED' : 'PREFERRED'}]
- Status: ${e.match_status}
- Citation: ${e.citation_source || 'Technical Skills'}
- Quote: "${e.evidence_quote || 'N/A'}"
- Explanation: ${e.explanation}
`
  )
  .join('\n')}
`;
    navigator.clipboard.writeText(reportText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Match Analysis &amp; Evidence Audit
            </h1>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Deterministic ∑ (w_i · s_i)
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Candidate: <span className="text-white font-semibold">{candidateProfile?.full_name}</span> • Role: <span className="text-white font-semibold">{jobData?.title}</span> at <span className="text-white font-semibold">{jobData?.company}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyReport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs font-medium transition-all"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied Markdown' : 'Copy Report'}</span>
          </button>
        </div>
      </div>

      {/* Synthesis Narrative Banner */}
      {synthesis_explanation && (
        <div className="glass-card rounded-2xl p-5 border border-indigo-500/30 bg-indigo-500/[0.03] space-y-2">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>EXECUTIVE SYNTHESIS &amp; RATIONALE</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed font-sans">
            {synthesis_explanation}
          </p>
        </div>
      )}

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Score Gauge Card */}
        <div className="lg:col-span-4 glass-card rounded-2xl p-6 border border-white/5 flex flex-col items-center justify-center text-center">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold mb-4">
            Composite Compatibility
          </h3>
          <ScoreGauge score={overall_score} size={190} title="Overall Fit" />
          <div className="grid grid-cols-2 gap-2 w-full mt-6 pt-4 border-t border-white/5 text-xs text-slate-400">
            <div className="p-2 rounded-lg bg-[#0B0F19]">
              <div className="text-[10px] font-mono text-slate-500">DIRECT VERIFIED</div>
              <div className="text-base font-bold text-emerald-400">{directCount}</div>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F19]">
              <div className="text-[10px] font-mono text-slate-500">TRANSFERABLE</div>
              <div className="text-base font-bold text-cyan-400">{transCount}</div>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F19]">
              <div className="text-[10px] font-mono text-slate-500">INFERRED</div>
              <div className="text-base font-bold text-indigo-400">{inferredCount}</div>
            </div>
            <div className="p-2 rounded-lg bg-[#0B0F19]">
              <div className="text-[10px] font-mono text-slate-500">MISSING GAPS</div>
              <div className="text-base font-bold text-rose-400">{missingCount}</div>
            </div>
          </div>
        </div>

        {/* Polar Radar Chart Card */}
        <div className="lg:col-span-8 glass-card rounded-2xl p-6 border border-white/5 flex flex-col items-center justify-between">
          <div className="w-full flex items-center justify-between mb-2">
            <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
              6-Factor Radar Profile
            </h3>
            <span className="text-[11px] font-mono text-slate-500">
              Normalized Dynamic Redistribution
            </span>
          </div>
          <div className="py-2">
            <PolarRadarChart breakdown={breakdown} size={320} />
          </div>
          <p className="text-[11px] text-slate-400 text-center font-mono mt-2">
            Each axis represents an independent mathematical feature score (0–100%)
          </p>
        </div>
      </div>

      {/* 8-Layer Mathematical Breakdown Table */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">
              Deterministic Mathematical Decomposition
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Exact formula: Score = ∑ (w_i · s_i). Dynamic weight redistribution ensures total weight ∑ w_i = 1.00.
            </p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
            Total: {overall_score}%
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 font-mono text-[11px]">
                <th className="pb-3 font-semibold">FACTOR / DIMENSION</th>
                <th className="pb-3 font-semibold">RAW SCORE (s_i)</th>
                <th className="pb-3 font-semibold">DYNAMIC WEIGHT (w_i)</th>
                <th className="pb-3 font-semibold text-right">WEIGHTED CONTRIBUTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {Object.entries(breakdown || {}).map(([key, item]) => (
                <tr key={key} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 font-medium text-slate-200">
                    {item.label}
                  </td>
                  <td className="py-3 font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold">{item.score}%</span>
                      <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-indigo-500 h-full rounded-full"
                          style={{ width: `${Math.min(100, item.score)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 font-mono text-slate-400">
                    {(item.weight * 100).toFixed(1)}% ({item.weight.toFixed(3)})
                  </td>
                  <td className="py-3 font-mono font-bold text-right text-emerald-400">
                    +{item.contribution}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Evidence Audit Matrix */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Qualification Evidence Matrix</span>
              <span className="text-xs font-mono text-slate-400 font-normal">
                ({filteredEvidences.length} of {evidences.length} shown)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Transparent, citation-backed status for each required and preferred qualification.
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Type Filter */}
            <div className="flex items-center bg-[#0B0F19] rounded-lg p-0.5 border border-white/5 text-[11px]">
              <button
                onClick={() => setFilterType('all')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  filterType === 'all' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All ({evidences.length})
              </button>
              <button
                onClick={() => setFilterType('required')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  filterType === 'required' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Required ({evidences.filter((e) => e.is_required).length})
              </button>
              <button
                onClick={() => setFilterType('preferred')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  filterType === 'preferred' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Preferred ({evidences.filter((e) => !e.is_required).length})
              </button>
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#0B0F19] border border-white/10 rounded-lg px-2.5 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-indigo-500 font-mono"
            >
              <option value="all">Status: All</option>
              <option value="direct_match">Direct Match</option>
              <option value="transferable_match">Transferable</option>
              <option value="inferred">Inferred</option>
              <option value="missing">Missing</option>
            </select>
          </div>
        </div>

        {/* Evidence Cards List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredEvidences.map((ev, idx) => (
            <EvidenceCard key={idx} evidence={ev} />
          ))}
          {filteredEvidences.length === 0 && (
            <div className="col-span-2 p-8 text-center glass-card rounded-2xl border border-white/5 text-slate-400 text-xs">
              No qualification items match the selected filter criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
