import React from 'react';
import { CheckCircle2, ArrowRightCircle, Sparkles, XCircle, FileText } from 'lucide-react';

export default function EvidenceCard({ evidence }) {
  const {
    skill_name,
    is_required,
    match_status,
    matched_candidate_skill,
    similarity_score,
    evidence_quote,
    explanation,
    citation_source,
  } = evidence;

  let badgeIcon = <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
  let badgeText = 'Direct Match';
  let badgeStyle = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';

  if (match_status === 'transferable_match') {
    badgeIcon = <ArrowRightCircle className="w-4 h-4 text-cyan-400" />;
    badgeText = `Transferable (${matched_candidate_skill || 'Adjacent'})`;
    badgeStyle = 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
  } else if (match_status === 'inferred') {
    badgeIcon = <Sparkles className="w-4 h-4 text-indigo-400" />;
    badgeText = 'Inferred from Experience';
    badgeStyle = 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30';
  } else if (match_status === 'missing') {
    badgeIcon = <XCircle className="w-4 h-4 text-rose-400" />;
    badgeText = 'Missing Qualification';
    badgeStyle = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
  }

  return (
    <div className="glass-card rounded-xl p-4 border transition-all">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-base font-bold text-white tracking-wide">
            {skill_name}
          </span>
          <span
            className={`px-2 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider ${
              is_required
                ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                : 'bg-slate-700/50 text-slate-400 border border-slate-600/30'
            }`}
          >
            {is_required ? 'Required' : 'Preferred'}
          </span>
        </div>

        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${badgeStyle}`}>
          {badgeIcon}
          <span>{badgeText}</span>
          {similarity_score !== undefined && similarity_score > 0 && (
            <span className="text-[10px] font-mono opacity-80 ml-1">
              {(similarity_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>

      {explanation && (
        <p className="text-sm text-slate-300 leading-relaxed mb-3">
          {explanation}
        </p>
      )}

      {evidence_quote && (
        <div className="bg-[#0B0F19]/80 border-l-2 border-indigo-500 rounded-r-lg p-2.5 my-2">
          <p className="text-xs text-slate-300 italic font-sans leading-relaxed">
            "{evidence_quote}"
          </p>
        </div>
      )}

      {citation_source && (
        <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-white/5 text-[11px] text-slate-400 font-mono">
          <FileText className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
          <span className="text-slate-500">Source:</span>
          <span className="text-slate-300 truncate">{citation_source}</span>
        </div>
      )}
    </div>
  );
}

