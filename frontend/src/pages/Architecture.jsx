import React from 'react';
import {
  Network,
  Cpu,
  Layers,
  Shield,
  Zap,
  Lock,
  ArrowRight,
  Database,
  Server,
  Monitor
} from 'lucide-react';

export default function Architecture() {
  const pipelineSteps = [
    {
      num: '01',
      title: 'Document Ingestion & Parsing',
      tech: 'PyMuPDF (fitz) / python-docx',
      desc: 'Extracts raw text and metadata from PDF, DOCX, and TXT files with byte-level validation and 15MB upload limits.',
    },
    {
      num: '02',
      title: 'Sanitization & Section Segmentation',
      tech: 'Regex Boundary Automata',
      desc: 'Cleans null bytes and control characters. Dynamically partitions text into header, experience, education, projects, and skills.',
    },
    {
      num: '03',
      title: 'Skill Extraction & Canonical Normalization',
      tech: '36 Canonical Nodes + 125 Aliases',
      desc: 'Matches surface forms (e.g., "JS", "ECMAScript", "ES6") to immutable canonical taxonomy IDs with transferability edges.',
    },
    {
      num: '04',
      title: 'Dense Semantic Encoding',
      tech: 'sentence-transformers/all-MiniLM-L6-v2',
      desc: 'Encodes 384-dimensional dense semantic vectors locally. Computes cosine similarity across resume sentences and job requisitions.',
    },
    {
      num: '05',
      title: '8-Layer Explainable Decomposition',
      tech: 'Dynamic Weight Redistribution',
      desc: 'Calculates overall compatibility via sum(w_i * s_i). If a requisition lacks education or experience requirements, weights dynamically normalize to 1.00.',
    },
    {
      num: '06',
      title: 'Evidence & Citation Grounding',
      tech: 'Quote Verification Engine',
      desc: 'Attaches exact sentence quotes and section header paths (Resume -> Experience -> Role @ Company) to eliminate hallucinations.',
    },
    {
      num: '07',
      title: 'FastAPI Decoupled REST Service',
      tech: 'Python 3.13 + Uvicorn + Pydantic v2',
      desc: 'Provides 10 type-safe REST endpoints with CORS policies, OpenAPI docs, and sub-second execution.',
    },
    {
      num: '08',
      title: 'React + Vite Frontend Client',
      tech: 'React 18 + Tailwind CSS + Lucide',
      desc: 'Stateless, reactive dark-mode interface with SVG radar charts, circular score gauges, and evidence audit matrix.',
    },
  ];

  const tradeOffs = [
    {
      decision: 'Local Embeddings (all-MiniLM-L6-v2) vs. Cloud LLM APIs',
      chosen: 'Local 384-dim Dense Model',
      rationale:
        'Zero API egress costs, deterministic latency (< 25ms vs. 2000ms+ for cloud LLMs), complete candidate data privacy (PII never leaves the server), and reproducible similarity scores.',
    },
    {
      decision: '8-Layer Mathematical Scoring vs. Single Black-Box LLM Score',
      chosen: 'Decomposed Weighted Sum (sum w_i * s_i)',
      rationale:
        'Prevents recruitment bias and hallucination. Every percentage point is traceable to specific qualifications, experience ratios, or semantic alignment. Weights dynamically redistribute if requirements are omitted.',
    },
    {
      decision: 'Canonical Taxonomy Graph vs. Pure String Keyword Matching',
      chosen: '36-Node Ontology with 125 Aliases',
      rationale:
        'Pure string matching catastrophically fails on aliases ("PyTorch" vs "torch", "K8s" vs "Kubernetes") and conflates unrelated concepts ("Java" vs "JavaScript"). Our taxonomy models adjacent transferability (e.g. PyTorch -> TensorFlow at 0.70x credit).',
    },
    {
      decision: 'In-Memory Stateless Execution vs. Persistent Candidate Database',
      chosen: 'Stateless REST Architecture',
      rationale:
        'Candidate resumes frequently contain sensitive PII (contact numbers, home addresses). Processing in volatile memory with zero disk persistence guarantees compliance and eliminates database leakage attack surfaces.',
    },
  ];

  return (
    <div className="space-y-10 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            System Architecture &amp; Design Decisions
          </h1>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            Decoupled REST + ML
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Detailed breakdown of the data processing pipeline, mathematical scoring algorithms, and engineering trade-offs.
        </p>
      </div>

      {/* High-Level Topology Diagram */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 space-y-4">
        <h2 className="text-sm font-mono uppercase tracking-wider text-slate-400 font-semibold">
          High-Level Decoupled Architecture Topology
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-5 rounded-xl bg-[#0B0F19] border border-white/10 space-y-2">
            <Monitor className="w-6 h-6 text-indigo-400 mx-auto" />
            <h3 className="text-sm font-bold text-white">Client Tier (Vercel)</h3>
            <p className="text-xs text-slate-400">
              React 18 SPA + Vite + Tailwind CSS. Responsive SVG radar charts, score gauges, interactive evidence filters.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[#0B0F19] border border-indigo-500/30 glow-indigo space-y-2">
            <Server className="w-6 h-6 text-emerald-400 mx-auto" />
            <h3 className="text-sm font-bold text-white">API Tier (FastAPI / Render)</h3>
            <p className="text-xs text-slate-400">
              High-concurrency ASGI server (Uvicorn). Pydantic v2 validation, multipart document upload, CORS middleware.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-[#0B0F19] border border-white/10 space-y-2">
            <Cpu className="w-6 h-6 text-purple-400 mx-auto" />
            <h3 className="text-sm font-bold text-white">AI/ML Core Engine</h3>
            <p className="text-xs text-slate-400">
              PyMuPDF parser, sentence-transformers/all-MiniLM-L6-v2 (384-dim), 36-skill taxonomy graph, 8-layer matching engine.
            </p>
          </div>
        </div>
      </div>

      {/* End-to-End Pipeline Steps */}
      <div className="space-y-4">
        <h2 className="text-sm font-mono uppercase tracking-wider text-slate-400 font-semibold">
          End-to-End Execution Pipeline (8 Stages)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {pipelineSteps.map((step, idx) => (
            <div key={idx} className="glass-card rounded-2xl p-5 border border-white/5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-indigo-400">{step.num}</span>
                <span className="text-[10px] font-mono text-slate-500 truncate max-w-[150px]">{step.tech}</span>
              </div>
              <h3 className="text-sm font-bold text-white">{step.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Key Architectural Trade-Offs Table */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 space-y-4">
        <h2 className="text-sm font-mono uppercase tracking-wider text-slate-400 font-semibold">
          Key Engineering Trade-Offs &amp; Technical Rationale
        </h2>

        <div className="space-y-4">
          {tradeOffs.map((item, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                <span className="font-bold text-white">{item.decision}</span>
                <span className="font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 w-fit">
                  Chosen: {item.chosen}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed pt-1">
                {item.rationale}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Privacy & Security Guarantees */}
      <div className="glass-card rounded-2xl p-6 border border-white/5 space-y-4">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
          <Shield className="w-4 h-4 text-indigo-400" />
          <span>PRIVACY &amp; SECURITY PROTOCOLS</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <Lock className="w-4 h-4 text-emerald-400" />
            <h4 className="font-bold text-white">Volatile Memory Processing</h4>
            <p className="text-slate-400 leading-relaxed">
              Resume files are processed in-memory as byte streams. Zero disk writes or database logging of candidate PII.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <Zap className="w-4 h-4 text-cyan-400" />
            <h4 className="font-bold text-white">Local Inference Isolation</h4>
            <p className="text-slate-400 leading-relaxed">
              Embeddings and NLP extractors run locally within the Python process. No resume snippets are sent to third-party cloud APIs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#0B0F19] border border-white/5 space-y-1.5">
            <Layers className="w-4 h-4 text-purple-400" />
            <h4 className="font-bold text-white">Input Sanitization Guardrails</h4>
            <p className="text-slate-400 leading-relaxed">
              Null byte stripping, Unicode normalization, file type validation, and 15MB payload size caps prevent memory exhaustion attacks.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

