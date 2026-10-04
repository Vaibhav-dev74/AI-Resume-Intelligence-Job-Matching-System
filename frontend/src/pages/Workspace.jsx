import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  UploadCloud,
  FileText,
  Briefcase,
  User,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Code
} from 'lucide-react';

export default function Workspace() {
  const {
    presets,
    candidateProfile,
    setCandidateProfile,
    candidateRawText,
    setCandidateRawText,
    candidateFilename,
    setCandidateFilename,
    jobData,
    setJobData,
    jobRawText,
    setJobRawText,
    selectPresetResume,
    selectPresetJob,
    executeMatch,
    loading,
    error,
    setError
  } = useApp();

  const [resumeMode, setResumeMode] = useState('preset'); // 'upload' | 'preset' | 'text'
  const [jobMode, setJobMode] = useState('preset'); // 'preset' | 'text'
  const [parsingResume, setParsingResume] = useState(false);
  const [parsingJob, setParsingJob] = useState(false);

  // File Upload Handler
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setParsingResume(true);
    setError(null);
    try {
      const profile = await api.analyzeResumeFile(file);
      setCandidateProfile(profile);
      setCandidateFilename(file.name);
      setCandidateRawText(`[Extracted from binary document: ${file.name}]`);
    } catch (err) {
      setError(`Failed to parse ${file.name}: ${err.message}`);
    } finally {
      setParsingResume(false);
    }
  };

  // Resume Text Analysis Handler
  const handleResumeTextSubmit = async () => {
    if (!candidateRawText.trim()) return;
    setParsingResume(true);
    setError(null);
    try {
      const profile = await api.analyzeResumeText(candidateRawText, candidateFilename || 'resume.txt');
      setCandidateProfile(profile);
    } catch (err) {
      setError(`Failed to extract resume text: ${err.message}`);
    } finally {
      setParsingResume(false);
    }
  };

  // Job Text Analysis Handler
  const handleJobTextSubmit = async () => {
    if (!jobRawText.trim()) return;
    setParsingJob(true);
    setError(null);
    try {
      const parsed = await api.analyzeJob(jobRawText);
      setJobData(parsed);
    } catch (err) {
      setError(`Failed to parse job description: ${err.message}`);
    } finally {
      setParsingJob(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            AI Match Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Upload or select candidate resumes &amp; target job requisitions for deterministic 8-layer qualification matching.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {(candidateProfile || jobData) && (
            <button
              onClick={() => {
                setCandidateProfile(null);
                setCandidateRawText('');
                setJobData(null);
                setJobRawText('');
                setError(null);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 text-xs transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset All</span>
            </button>
          )}

          <button
            onClick={() => executeMatch()}
            disabled={!candidateProfile || !jobData || loading}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-semibold text-xs shadow-lg glow-emerald disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>{loading ? 'Executing Engine...' : 'Calculate 8-Layer Match'}</span>
          </button>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-xs">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Dual Input Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Candidate Resume Input */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-mono uppercase tracking-wider text-slate-200 font-semibold">
                Candidate Resume
              </h2>
            </div>

            {/* Mode Selector */}
            <div className="flex items-center bg-[#0B0F19] rounded-lg p-0.5 border border-white/5 text-[11px]">
              <button
                onClick={() => setResumeMode('preset')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  resumeMode === 'preset' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Presets
              </button>
              <button
                onClick={() => setResumeMode('upload')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  resumeMode === 'upload' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Upload File
              </button>
              <button
                onClick={() => setResumeMode('text')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  resumeMode === 'text' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Raw Text
              </button>
            </div>
          </div>

          {/* Mode Body */}
          {resumeMode === 'preset' && (
            <div className="glass-card rounded-2xl p-4 border border-white/5 space-y-2">
              <label className="text-xs text-slate-400 font-medium block">
                Select Curated Golden Candidate:
              </label>
              <div className="space-y-2">
                {Object.keys(presets.resumes || {}).map((name) => {
                  const isSelected = candidateProfile?.full_name && name.includes(candidateProfile.full_name);
                  return (
                    <button
                      key={name}
                      onClick={() => selectPresetResume(name)}
                      className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                        isSelected
                          ? 'bg-indigo-600/20 border-indigo-500/40 text-white glow-indigo'
                          : 'bg-[#0B0F19]/60 border-white/5 text-slate-300 hover:border-white/10 hover:bg-white/[0.02]'
                      }`}
                    >
                      <div className="font-semibold text-white">{name}</div>
                      <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                        {presets.resumes[name].raw_text.slice(0, 100)}...
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {resumeMode === 'upload' && (
            <div className="glass-card rounded-2xl p-6 border border-dashed border-white/15 text-center hover:border-indigo-500/40 transition-colors">
              <input
                type="file"
                id="resume-file-input"
                accept=".pdf,.docx,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
              <label htmlFor="resume-file-input" className="cursor-pointer space-y-3 block">
                <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/30 mx-auto flex items-center justify-center">
                  <UploadCloud className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                  <span className="text-sm font-semibold text-white">Click to upload resume</span>
                  <p className="text-xs text-slate-400 mt-0.5">Supports PDF, DOCX, and TXT files (Max 15MB)</p>
                </div>
                {parsingResume && (
                  <div className="text-xs font-mono text-indigo-400 animate-pulse">
                    Extracting text with PyMuPDF &amp; segmenting sections...
                  </div>
                )}
              </label>
            </div>
          )}

          {resumeMode === 'text' && (
            <div className="glass-card rounded-2xl p-4 border border-white/5 space-y-3">
              <textarea
                rows={7}
                value={candidateRawText}
                onChange={(e) => setCandidateRawText(e.target.value)}
                placeholder="Paste unstructured candidate resume text here..."
                className="w-full bg-[#0B0F19] border border-white/10 rounded-xl p-3 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
              />
              <button
                onClick={handleResumeTextSubmit}
                disabled={parsingResume || !candidateRawText.trim()}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all disabled:opacity-50"
              >
                {parsingResume ? 'Analyzing...' : 'Parse Resume Text'}
              </button>
            </div>
          )}

          {/* Parsed Candidate Profile Preview */}
          {candidateProfile && (
            <div className="glass-card rounded-2xl p-5 border border-emerald-500/20 bg-emerald-500/[0.02] space-y-3">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>{candidateProfile.full_name || 'Candidate'}</span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  </h3>
                  <p className="text-xs text-slate-400">
                    {candidateProfile.inferred_primary_role || 'Software Engineer'} • {candidateProfile.total_years_experience || 0} Years Experience
                  </p>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {candidateProfile.skills?.length || 0} Skills Extracted
                </span>
              </div>

              {/* Skills Tags */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-mono text-slate-400">EXTRACTED ONTOLOGY SKILLS:</span>
                <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto pr-1">
                  {candidateProfile.skills?.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] font-mono"
                    >
                      {s.canonical_name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Job Requisition Input */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-mono uppercase tracking-wider text-slate-200 font-semibold">
                Target Job Requisition
              </h2>
            </div>

            {/* Job Mode Selector */}
            <div className="flex items-center bg-[#0B0F19] rounded-lg p-0.5 border border-white/5 text-[11px]">
              <button
                onClick={() => setJobMode('preset')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  jobMode === 'preset' ? 'bg-emerald-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Presets
              </button>
              <button
                onClick={() => setJobMode('text')}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  jobMode === 'text' ? 'bg-emerald-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Custom Job Text
              </button>
            </div>
          </div>

          {/* Job Mode Body */}
          {jobMode === 'preset' && (
            <div className="glass-card rounded-2xl p-4 border border-white/5 space-y-2">
              <label className="text-xs text-slate-400 font-medium block">
                Select Benchmark Job Requisition:
              </label>
              <div className="space-y-2">
                {Object.keys(presets.jobs || {}).map((name) => {
                  const isSelected = jobData?.title && name.includes(jobData.title);
                  return (
                    <button
                      key={name}
                      onClick={() => selectPresetJob(name)}
                      className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                        isSelected
                          ? 'bg-emerald-600/20 border-emerald-500/40 text-white glow-emerald'
                          : 'bg-[#0B0F19]/60 border-white/5 text-slate-300 hover:border-white/10 hover:bg-white/[0.02]'
                      }`}
                    >
                      <div className="font-semibold text-white">{name}</div>
                      <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                        {presets.jobs[name].raw_text.slice(0, 100)}...
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {jobMode === 'text' && (
            <div className="glass-card rounded-2xl p-4 border border-white/5 space-y-3">
              <textarea
                rows={7}
                value={jobRawText}
                onChange={(e) => setJobRawText(e.target.value)}
                placeholder="Paste job description (Include sections like 'Required Qualifications' and 'Preferred Skills')..."
                className="w-full bg-[#0B0F19] border border-white/10 rounded-xl p-3 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-emerald-500 font-mono"
              />
              <button
                onClick={handleJobTextSubmit}
                disabled={parsingJob || !jobRawText.trim()}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-all disabled:opacity-50"
              >
                {parsingJob ? 'Analyzing...' : 'Parse Job Requirements'}
              </button>
            </div>
          )}

          {/* Parsed Job Requisition Preview */}
          {jobData && (
            <div className="glass-card rounded-2xl p-5 border border-indigo-500/20 bg-indigo-500/[0.02] space-y-3">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>{jobData.title || 'Target Role'}</span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  </h3>
                  <p className="text-xs text-slate-400">
                    {jobData.company || 'Hiring Organization'} • Min {jobData.min_years_experience || 0} Years Exp Target
                  </p>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {jobData.required_skills?.length || 0} Required • {jobData.preferred_skills?.length || 0} Preferred
                </span>
              </div>

              {/* Required Skills */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-mono text-amber-400">REQUIRED QUALIFICATIONS:</span>
                <div className="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto pr-1">
                  {jobData.required_skills?.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] font-mono"
                    >
                      {typeof s === 'string' ? s : s.canonical_name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Preferred Skills */}
              {jobData.preferred_skills?.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-mono text-slate-400">PREFERRED SKILLS:</span>
                  <div className="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto pr-1">
                    {jobData.preferred_skills?.map((s, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded-md bg-slate-700/50 border border-slate-600/30 text-slate-300 text-[11px] font-mono"
                      >
                        {typeof s === 'string' ? s : s.canonical_name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

