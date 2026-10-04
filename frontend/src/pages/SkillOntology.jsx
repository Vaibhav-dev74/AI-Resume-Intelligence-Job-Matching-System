import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  Binary,
  Search,
  Tag,
  ArrowRight,
  Filter,
  CheckCircle,
  HelpCircle,
  Share2
} from 'lucide-react';

export default function SkillOntology() {
  const { canonicalSkills } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = ['all', 'programming_language', 'framework', 'cloud_devops', 'database', 'ai_ml', 'tool'];

  const filteredSkills = (canonicalSkills || []).filter((skill) => {
    const matchesCategory = selectedCategory === 'all' || skill.category === selectedCategory;
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch =
      !searchTerm ||
      skill.canonical_name.toLowerCase().includes(searchLower) ||
      (skill.aliases && skill.aliases.some((a) => a.toLowerCase().includes(searchLower))) ||
      (skill.description && skill.description.toLowerCase().includes(searchLower));

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Canonical Skill Ontology &amp; Taxonomy Graph
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
            36 Nodes • 125 Aliases
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Eliminates surface-form vocabulary mismatch by mapping raw resume tokens to curated canonical concepts with weighted transferability edges.
        </p>
      </div>

      {/* Concept Explanation Card */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 space-y-4">
        <h2 className="text-sm font-mono uppercase tracking-wider text-slate-400 font-semibold">
          Why Skill Normalization is Critical for Resume Intelligence
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <span className="font-bold text-rose-400 block font-mono text-[11px]">1. FLAGGING VOCABULARY MISMATCH</span>
            <p className="text-slate-300 leading-relaxed">
              A candidate writing <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">K8s</code> or <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">FastAPI framework</code> would be rejected by legacy ATS systems expecting exact string "Kubernetes". Aliases resolve this instantly.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <span className="font-bold text-amber-400 block font-mono text-[11px]">2. PREVENTING FALSE POSITIVES</span>
            <p className="text-slate-300 leading-relaxed">
              Unconstrained embeddings frequently confuse unrelated words with similar character n-grams (e.g. <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">Java</code> vs <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">JavaScript</code>). Canonical nodes enforce strict semantic boundaries.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <span className="font-bold text-emerald-400 block font-mono text-[11px]">3. TRANSFERABILITY CREDITING</span>
            <p className="text-slate-300 leading-relaxed">
              If a role requires <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">TensorFlow</code> and the candidate demonstrates deep <code className="bg-slate-800 text-indigo-300 px-1 py-0.5 rounded">PyTorch</code> mastery, our taxonomy credits this as a 0.70x transferable match instead of a total penalty.
            </p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search skills, aliases (e.g. k8s, torch, postgres)..."
            className="w-full bg-[#0B0F19] border border-white/10 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>

        {/* Category Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 text-xs">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg border text-xs whitespace-nowrap capitalize transition-all ${
                selectedCategory === cat
                  ? 'bg-indigo-600 border-indigo-500 text-white font-medium glow-indigo'
                  : 'bg-[#0B0F19] border-white/5 text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Taxonomy Skill Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSkills.map((skill, idx) => (
          <div key={idx} className="glass-card rounded-2xl p-5 border border-white/5 space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-base font-bold text-white tracking-wide">
                  {skill.canonical_name}
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 capitalize">
                  {skill.category?.replace('_', ' ')}
                </span>
              </div>

              {skill.description && (
                <p className="text-xs text-slate-300 leading-relaxed">
                  {skill.description}
                </p>
              )}
            </div>

            <div className="space-y-2 pt-2 border-t border-white/5">
              {/* Aliases */}
              {skill.aliases?.length > 0 && (
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
                    Normalized Aliases:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {skill.aliases.map((al, aIdx) => (
                      <span key={aIdx} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50">
                        {al}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Transferable Edges */}
              {skill.transferable_to && Object.keys(skill.transferable_to).length > 0 && (
                <div className="pt-1">
                  <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block mb-1">
                    Transferable Edges:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(skill.transferable_to).map(([tName, weight], tIdx) => (
                      <span key={tIdx} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 flex items-center gap-1">
                        <span>{tName}</span>
                        <span className="text-[9px] opacity-75">({weight}x)</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {filteredSkills.length === 0 && (
          <div className="col-span-3 p-12 text-center glass-card rounded-2xl border border-white/5 text-slate-400 text-xs">
            No canonical skills found matching the search criteria.
          </div>
        )}
      </div>
    </div>
  );
}

