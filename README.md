# IntelliResume AI — AI Resume Intelligence & Job Matching Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20App-black?style=flat&logo=vercel)](https://ai-resume-intelligence-job-matching.vercel.app/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.4-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Tests: Pytest](https://img.shields.io/badge/Pytest-43%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Production-grade AI platform combining deterministic NLP, canonical skill ontologies, and dense semantic embeddings to explain exactly why and how a candidate matches a job requisition—backed by verbatim citations and empirical benchmarks.**

**Live Application**: [https://ai-resume-intelligence-job-matching.vercel.app/](https://ai-resume-intelligence-job-matching.vercel.app/)

---

## 💡 Key Architectural Highlights

* **100% Deterministic & Explainable**: Replaces stochastic, hallucination-prone LLM prompts with an explainable linear compatibility model: $\text{Score} = 100 \times \sum w_i \cdot s_i$.
* **Canonical Skill Taxonomy**: 36 canonical technical nodes with 125 aliases and weighted transferability edges (e.g. `Flask` $\to$ `FastAPI` at 0.85 transferability).
* **Verbatim Evidence Grounding**: Every direct and transferable match links to literal textual citations from candidate documents, preventing fabricated claims.
* **Dynamic Weight Redistribution**: Automatically renormalizes weights ($\sum w_i' = 1.00$) when jobs omit preferred skills or candidates lack explicit project sections.
* **Privacy-First Zero Retention**: In-memory ephemeral document parsing with automated PII scrubbing (emails, phone numbers, blind screening mode).

---

## 🏗️ System Architecture

```
[ Client Browser ] ──HTTPS──▶ [ React 18 + Vite SPA (Vercel) ]
                                      │  REST JSON / Multipart
                                      ▼
                        [ FastAPI REST Backend (Render) ]
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
[ Document Parser ]         [ AI & Semantic Engine ]       [ Recommendations ]
• PyMuPDF / docx            • 36-Skill Canonical Graph     • 4-Week Skill Roadmap
• NFKD Ligature Clean       • all-MiniLM-L6-v2 Embeddings  • Bullet Optimizer
• Upload Magic-Bytes        • Dynamic Linear Matcher       • Cosine Role Matcher
```

---

## 🔬 Scoring Model & Empirical Benchmarks

$$\text{Overall Compatibility} = 100 \times \left( 0.40\,S_{\text{req}} + 0.20\,S_{\text{sem}} + 0.15\,S_{\text{exp}} + 0.10\,S_{\text{pref}} + 0.10\,S_{\text{proj}} + 0.05\,S_{\text{edu}} \right)$$

Evaluated offline across **12 gold-standard benchmark pairs** (85 annotated skills, 44 requirement checks):

| Metric | Measured Score | Significance |
|---|---|---|
| **Skill Extraction Precision** | **94.1%** | Prevents false-positive skill hallucinations |
| **Skill Extraction Recall** | **91.8%** | Captures genuine candidate competencies |
| **Skill Extraction F1-Score** | **0.929** | High balanced extraction accuracy |
| **Job Requirement Accuracy** | **93.2%** | Correct Direct / Transferable / Missing classification |
| **Semantic Retrieval MRR** | **0.750** | Mean Reciprocal Rank on candidate-role search |
| **Mean Inference Latency** | **~38 ms** | Fast local CPU execution with model caching |

---

## 🔌 Production REST API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health status and model readiness |
| `GET` | `/api/presets` | Synthetic demo candidate profiles & jobs |
| `GET` | `/api/skills/canonical` | 36 canonical ontology nodes with transfer graph |
| `POST` | `/api/resume/analyze` | Multipart document parser (`.pdf`, `.docx`, `.txt`) |
| `POST` | `/api/resume/analyze-json`| Raw text resume extractor |
| `POST` | `/api/job/analyze` | Job requisition requirement extractor |
| `POST` | `/api/match` | 8-layer explainable compatibility matcher |
| `POST` | `/api/skill-gaps` | Skill gap analysis and 4-week upskilling roadmap |
| `POST` | `/api/resume/improve` | Evidence-grounded resume bullet optimizer |
| `POST` | `/api/recommendations` | Dense cosine role recommender |
| `GET` / `POST` | `/api/evaluation` | Offline benchmark suite inspection & live run |

---

## 💻 Local Quickstart

### 1. Backend (FastAPI)
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```
* Interactive API Docs: `http://localhost:8000/docs`

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
* Web Application: `http://localhost:5173`

### 3. Automated Test Suite (43 Tests)
```bash
pytest -v
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
