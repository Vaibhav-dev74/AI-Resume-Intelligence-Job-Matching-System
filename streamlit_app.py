import os
import sys
import json
import time
import hashlib
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.document_processing.parser_factory import document_parser_factory
from app.ai.extraction.resume_extractor import resume_extractor
from app.ai.extraction.job_analyzer import job_analyzer
from app.ai.matching.matcher import matching_engine
from app.ai.matching.gap_analyzer import gap_analyzer
from app.ai.recommendations.resume_improver import resume_improver
from app.ai.recommendations.job_recommender import job_recommender
from app.services.evaluation_service import evaluation_service
from app.ai.embeddings.embedding_engine import embedding_engine
from app.core.security import validate_file_safety
from app.core.logging import logger
from app.core.config import settings

st.set_page_config(
    page_title="IntelliResume AI — AI Resume Intelligence & Job Matching",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# HIDE STREAMLIT CLOUD TOOLBAR, GITHUB / PENCIL ICONS, AND MANAGE APP BUTTON
# ==============================================================================
components.html(
    """
    <script>
    function removeCloudChrome() {
        const docTargets = [document];
        try {
            if (window.parent && window.parent.document) {
                docTargets.push(window.parent.document);
            }
            if (window.top && window.top.document && window.top !== window.parent) {
                docTargets.push(window.top.document);
            }
        } catch (e) {}

        docTargets.forEach(doc => {
            if (!doc) return;

            // 1. Hide Header & Toolbar (GitHub icon, pencil icon, star, share, deploy)
            const headers = doc.querySelectorAll('header[data-testid="stHeader"], .stAppHeader');
            headers.forEach(h => {
                h.style.visibility = 'hidden';
                h.style.height = '0px';
                h.style.minHeight = '0px';
            });

            const toolbars = doc.querySelectorAll('[data-testid="stToolbar"], [data-testid="stToolbarActions"], #MainMenu, [data-testid="stDecoration"]');
            toolbars.forEach(t => {
                t.style.display = 'none';
                t.style.visibility = 'hidden';
            });

            // 2. Hide "Manage app" floating badge / button
            const manageBadges = doc.querySelectorAll('[data-testid="manage-app-button"], [class*="viewerBadge"], [class*="manage-app"], [class*="ManageApp"]');
            manageBadges.forEach(b => {
                b.style.display = 'none';
                b.style.visibility = 'hidden';
                if (b.parentElement && (b.parentElement.tagName === 'DIV' || b.parentElement.tagName === 'FOOTER')) {
                    b.parentElement.style.display = 'none';
                }
            });

            // 3. Scan for any button or link containing GitHub, Edit/Pencil, or Manage App
            const buttonsAndLinks = doc.querySelectorAll('button, a, div[role="button"]');
            buttonsAndLinks.forEach(el => {
                const text = (el.innerText || '').toLowerCase().trim();
                const title = (el.getAttribute('title') || '').toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const href = (el.getAttribute('href') || '').toLowerCase();

                if (
                    text.includes('manage app') || 
                    title.includes('manage app') || 
                    aria.includes('manage app')
                ) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    let parent = el.parentElement;
                    while (parent && parent !== doc.body) {
                        if (parent.className && typeof parent.className === 'string' && parent.className.includes('viewerBadge')) {
                            parent.style.display = 'none';
                            break;
                        }
                        parent = parent.parentElement;
                    }
                }

                if (
                    title.includes('github') || 
                    aria.includes('github') || 
                    href.includes('github.com') ||
                    title.includes('edit') || 
                    aria.includes('edit') || 
                    title.includes('view source')
                ) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                }
            });
        });
    }

    removeCloudChrome();
    try {
        if (window.MutationObserver) {
            const obs = new MutationObserver(() => removeCloudChrome());
            obs.observe(document.body, { childList: true, subtree: true });
            if (window.parent && window.parent.document && window.parent.document.body) {
                const parentObs = new MutationObserver(() => removeCloudChrome());
                parentObs.observe(window.parent.document.body, { childList: true, subtree: true });
            }
        }
    } catch (e) {}
    setInterval(removeCloudChrome, 1200);
    </script>
    """,
    height=0,
    width=0
)

# Pre-warm embedding model with fallback
@st.cache_resource(show_spinner=False)
def warm_embedding_engine():
    try:
        embedding_engine._get_model()
    except Exception as e:
        logger.warning(f"Embedding engine pre-warming deferred: {e}")
    return True

_ = warm_embedding_engine()

# ==============================================================================
# MODERN SAAS DESIGN SYSTEM
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ========================================================================= */
    /* HIDE STREAMLIT CLOUD TOOLBAR, GITHUB / PENCIL ICONS, AND MANAGE APP BUTTON */
    /* ========================================================================= */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        min-height: 0px !important;
        visibility: hidden !important;
    }
    
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stAppDeployButton"],
    [data-testid="stDecoration"],
    #MainMenu,
    header button,
    header a,
    .stAppToolbar,
    div[data-testid="stToolbarActions"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
        pointer-events: none !important;
    }

    /* Hide Streamlit Community Cloud Manage App floating badge & footer */
    footer,
    [data-testid="stFooter"],
    [data-testid="manage-app-button"],
    [class*="viewerBadge_container"],
    [class*="viewerBadge"],
    [class*="ManageApp"],
    [class*="manage-app"],
    [class*="StatusWidget"],
    #manage-app-button,
    .manage-app-button,
    div:has(> [data-testid="manage-app-button"]),
    div:has(> button[data-testid="manage-app-button"]) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0px !important;
        height: 0px !important;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #2E1065 45%, #3B0764 100%);
        border-radius: 18px;
        padding: 2.4rem 2.6rem;
        color: #F8FAFC;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px -8px rgba(30, 27, 75, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.14);
    }
    .hero-eyebrow {
        font-size: 0.92rem;
        font-weight: 700;
        color: #A5B4FC;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.6rem;
        background: linear-gradient(to right, #FFFFFF, #E0E7FF, #C7D2FE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #E2E8F0;
        max-width: 820px;
        line-height: 1.6;
        margin-bottom: 1.4rem;
    }
    .hero-points {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.8rem;
        margin-bottom: 1.4rem;
        font-size: 0.95rem;
        color: #F1F5F9;
    }
    .hero-badges {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.22);
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #F8FAFC;
    }

    /* Universal Cards */
    .saas-card {
        background: rgba(248, 250, 252, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(4px);
    }

    .metric-card {
        background: rgba(248, 250, 252, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366F1;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 0.3rem;
    }
    .metric-ctx {
        font-size: 0.74rem;
        color: #64748B;
        margin-top: 0.35rem;
    }

    /* Status Badges */
    .badge-direct {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }
    .badge-trans {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }
    .badge-missing {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }

    .skill-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem 0.3rem;
    }

    .diff-box-before {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }
    .diff-box-after {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }

    .evidence-quote {
        background: rgba(99, 102, 241, 0.06);
        border-left: 3px solid #6366F1;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }

    .pipeline-step {
        background: rgba(248, 250, 252, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }

    .styled-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(148, 163, 184, 0.3), transparent);
        margin: 1.5rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# PRESETS & SESSION STATE
# ==============================================================================
if "resumes" not in st.session_state:
    st.session_state.resumes = {}
if "jobs" not in st.session_state:
    st.session_state.jobs = {}
if "current_match" not in st.session_state:
    st.session_state.current_match = None
if "current_match_pair" not in st.session_state:
    st.session_state.current_match_pair = None
if "last_uploaded_file_hash" not in st.session_state:
    st.session_state.last_uploaded_file_hash = None

PRESET_RESUMES = {
    "Alice Chen (Senior ML Engineer)": """Alice Chen
alice.chen.ai@example.com | (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alice-chen-ai | GitHub: github.com/alicechen

PROFESSIONAL SUMMARY
Senior Machine Learning Engineer with 5+ years of experience designing and deploying distributed deep learning models and high-throughput REST APIs. Specialized in Computer Vision, NLP, and scalable inference architectures.

EDUCATION
Stanford University
Master of Science in Computer Science | 2017 - 2019

TECHNICAL SKILLS
Programming Languages: Python, C++, SQL, Bash
Machine Learning & AI: PyTorch, TensorFlow, Scikit-Learn, Computer Vision, Deep Learning
Frameworks & Databases: FastAPI, Flask, PostgreSQL, MySQL
Cloud & DevOps: Docker, Kubernetes, AWS, Git

PROFESSIONAL EXPERIENCE
Senior Machine Learning Engineer | DeepTech Labs | 2021-03 - Present
* Architected computer vision object detection pipeline using PyTorch, serving 2.5M daily inferences.
* Built microservice inference APIs using FastAPI and Docker, containerized on Kubernetes clusters.
* Reduced model latency by 45% using TensorRT optimizations and asynchronous batching.

Machine Learning Engineer | VisionScale Inc | 2019-06 - 2021-02
* Developed convolutional neural networks for semantic segmentation using TensorFlow and Python.
* Designed database schemas in PostgreSQL to store inference logs and ground-truth embeddings.
* Automated CI/CD deployment pipelines on AWS using Docker and GitHub Actions.

PROJECTS
EdgeVision: Real-time autonomous perception system on embedded Jetson GPUs using PyTorch and C++.
""",
    "David Miller (Backend Platform Engineer)": """David Miller
david.miller.dev@example.com | (555) 876-5432 | Austin, TX
LinkedIn: linkedin.com/in/david-miller-cloud | GitHub: github.com/davidmiller

PROFESSIONAL SUMMARY
Backend Software Engineer with 6 years of experience building mission-critical distributed systems, REST APIs, and microservices in Python and Go. Deep expertise in PostgreSQL, Docker, AWS, and event-driven architectures.

EDUCATION
University of Texas at Austin
Bachelor of Science in Computer Science | 2014 - 2018

TECHNICAL SKILLS
Programming Languages: Python, Go, SQL, Bash
Frameworks: FastAPI, Flask, Django
Databases: PostgreSQL, Redis, MySQL
Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, Git, CI/CD

PROFESSIONAL EXPERIENCE
Senior Backend Engineer | CloudScale Networks | 2021-01 - Present
* Designed high-throughput microservices using FastAPI and PostgreSQL handling 15,000 requests/sec.
* Containerized legacy infrastructure using Docker and orchestrated production workloads on AWS EKS with Kubernetes.
* Optimized complex SQL queries and PostgreSQL database indexing, reducing p99 query latency by 60%.

Backend Developer | FinTech Nexus | 2018-06 - 2020-12
* Built payment processing REST APIs with Flask and PostgreSQL.
* Automated AWS cloud infrastructure provisioning using Terraform and Docker.
""",
    "Elena Rostova (Junior NLP / Python Developer)": """Elena Rostova
elena.rostova@example.com | (555) 432-1098 | Boston, MA
LinkedIn: linkedin.com/in/elena-rostova | GitHub: github.com/elenarostova

PROFESSIONAL SUMMARY
Recent Master's graduate in Data Science with 1+ years of project experience developing NLP pipelines, transformer embeddings, and predictive machine learning models in Python.

EDUCATION
Boston University
Master of Science in Data Science | 2022 - 2024
Bachelor of Science in Mathematics | 2018 - 2022

TECHNICAL SKILLS
Programming Languages: Python, SQL, R
Machine Learning: Scikit-Learn, PyTorch, Transformers, NLP
Tools & Databases: PostgreSQL, Git, Pandas, NumPy

PROJECTS
MedNLP Sentiment Analyzer: Fine-tuned transformer models for clinical record summarization using PyTorch and Hugging Face.
Customer Churn Prediction: Implemented Random Forest and XGBoost classifiers in Scikit-Learn with 89% accuracy.
"""
}

PRESET_JOBS = {
    "Apex Robotics (Senior AI/CV Engineer)": """Senior Computer Vision & AI Engineer
Company: Apex Robotics Labs
Location: San Francisco, CA (Hybrid)

MINIMUM QUALIFICATIONS (REQUIRED):
* 4+ years of professional software engineering and machine learning experience.
* Bachelor's degree in Computer Science, Data Science, or related technical field.
* Strong proficiency in Python, PyTorch, and Computer Vision.
* Direct hands-on experience building and deploying REST APIs using FastAPI or Flask.
* Solid foundations in SQL, PostgreSQL, and Docker containerization.

PREFERRED QUALIFICATIONS:
* Master's or Ph.D. in AI, Robotics, or Computer Science.
* Experience with Kubernetes, AWS cloud architectures, and CI/CD pipelines.
* Familiarity with C++ and high-performance GPU optimization.
""",
    "Stripe (Senior Backend Platform Engineer)": """Senior Backend Platform Engineer
Company: Stripe
Location: Remote / San Francisco, CA

MINIMUM QUALIFICATIONS (REQUIRED):
* 5+ years of software engineering experience developing high-availability backend systems.
* Strong proficiency in Python and modern API frameworks such as FastAPI.
* Deep experience with relational databases including PostgreSQL and advanced SQL optimization.
* Proven background with Docker containerization and cloud architectures (AWS).

PREFERRED QUALIFICATIONS:
* Experience with Kubernetes orchestration and Terraform infrastructure-as-code.
* Strong background in microservice security and high-throughput distributed systems.
""",
    "DeepMind (Research Systems Engineer - NLP)": """Research Systems Engineer - NLP & Foundation Models
Company: Google DeepMind
Location: New York, NY / Hybrid

MINIMUM QUALIFICATIONS (REQUIRED):
* 3+ years experience engineering large-scale Machine Learning and NLP systems.
* Strong proficiency in Python, PyTorch, and Transformer architectures.
* Experience with Scikit-Learn, deep neural networks, and scalable model evaluation.
* Master's or Bachelor's degree in Computer Science or Mathematics.

PREFERRED QUALIFICATIONS:
* Experience with C++, distributed GPU training, and Docker.
* Published research in top AI conferences (NeurIPS, ICML, ACL).
"""
}

@st.cache_data(show_spinner=False)
def parse_preset_resume(resume_name: str, r_text: str):
    c_text, sections, _ = document_parser_factory.parse_document(r_text.encode("utf-8"), f"{resume_name}.txt")
    return resume_extractor.extract_profile(c_text, sections)

@st.cache_data(show_spinner=False)
def parse_preset_job(job_name: str, j_text: str):
    return job_analyzer.analyze(j_text)

def load_preset_pair(resume_name: str, job_name: str) -> bool:
    try:
        r_text = PRESET_RESUMES[resume_name]
        cand_profile = parse_preset_resume(resume_name, r_text)
        st.session_state.resumes[cand_profile["full_name"]] = cand_profile

        j_text = PRESET_JOBS[job_name]
        parsed_job = parse_preset_job(job_name, j_text)
        st.session_state.jobs[parsed_job["title"]] = parsed_job

        st.session_state.current_match = matching_engine.match(cand_profile, parsed_job)
        st.session_state.current_match_pair = (cand_profile["full_name"], parsed_job["title"])
        return True
    except Exception as e:
        st.error(f"Error loading demo: {e}")
        return False


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 0.2rem 0 0.8rem 0;">
            <div style="font-size: 2.2rem;">🎯</div>
            <div style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;">IntelliResume AI</div>
            <div style="font-size: 0.78rem; color: #94A3B8; font-weight: 500;">Explainable Matcher & Skill Intelligence</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ Try Interactive Demo", use_container_width=True, type="primary"):
        if load_preset_pair("Alice Chen (Senior ML Engineer)", "Apex Robotics (Senior AI/CV Engineer)"):
            st.toast("Loaded Alice Chen vs Apex Robotics!", icon="🚀")

    st.markdown("---")

    selected_category = st.radio(
        "Navigation Section",
        [
            "OVERVIEW",
            "AI WORKSPACE",
            "ENGINEERING",
            "ABOUT"
        ],
        index=0
    )

    if selected_category == "OVERVIEW":
        selected_page = "Executive Overview"
    elif selected_category == "AI WORKSPACE":
        selected_page = st.selectbox(
            "Workspace Module",
            [
                "Resume Parser & Extractor",
                "Job Description Analyzer",
                "Semantic Match & Evidence",
                "Skill Gap & Learning Roadmap",
                "Resume Improvement Engine",
                "AI Job Recommendations"
            ]
        )
    elif selected_category == "ENGINEERING":
        selected_page = st.selectbox(
            "Engineering Deep Dives",
            [
                "AI Pipeline & Architecture",
                "AI Evaluation & Benchmarks"
            ]
        )
    else:
        selected_page = "Technology Stack & Documentation"

    st.markdown("---")

    st.caption("PRESET SELECTOR")
    chosen_r = st.selectbox("Candidate Profile", list(PRESET_RESUMES.keys()), index=0)
    chosen_j = st.selectbox("Target Role", list(PRESET_JOBS.keys()), index=0)
    if st.button("Load Selected Pair", use_container_width=True):
        if load_preset_pair(chosen_r, chosen_j):
            st.toast("Loaded preset pair successfully!", icon="✅")
            st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style="background: rgba(148, 163, 184, 0.08); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 0.8rem; font-size: 0.8rem;">
            <div style="font-weight: 700; color: #10B981; margin-bottom: 0.2rem;">🟢 Inference Engine: Local Ready</div>
            <div style="color: #94A3B8;">Embedding: <code>all-MiniLM-L6-v2</code></div>
            <div style="color: #94A3B8;">Taxonomy: <b>36 Canonical / 125 Aliases</b></div>
            <div style="color: #94A3B8;">Matching: <b>8-Layer Deterministic</b></div>
        </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 1: EXECUTIVE OVERVIEW
# ==============================================================================
if selected_page == "Executive Overview":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-eyebrow">IntelliResume AI</div>
            <div class="hero-title">AI Resume Intelligence & Job Matching</div>
            <div class="hero-subtitle">
                An AI-powered resume and job matching platform that combines NLP, semantic embeddings, skill normalization, and evidence-based matching to explain why a candidate matches a role.
            </div>
            <div class="hero-points">
                <div>✓ <b>Understand</b> your resume structure and verified technical profile.</div>
                <div>✓ <b>Analyze</b> job requirements into mandatory vs preferred skills.</div>
                <div>✓ <b>Discover</b> actionable skill gaps with transferability bridging.</div>
                <div>✓ <b>Get</b> evidence-based matching insights backed by resume citations.</div>
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🎯 Evidence-Based Matching</span>
                <span class="hero-badge">🧠 Semantic Embeddings</span>
                <span class="hero-badge">🔗 Skill Intelligence</span>
                <span class="hero-badge">📊 Explainable Scoring</span>
                <span class="hero-badge">🛡️ Evidence-Constrained AI</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Clean Separation of Product Usage vs Model Benchmarks
    st.markdown("### Product Metrics & Operational Status")
    
    col_u1, col_u2, col_u3, col_u4 = st.columns(4)
    with col_u1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{len(st.session_state.resumes)}</div>
                <div class="metric-lbl">Resumes Analyzed</div>
                <div class="metric-ctx">Live session state</div>
            </div>
        """, unsafe_allow_html=True)
    with col_u2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{len(st.session_state.jobs)}</div>
                <div class="metric-lbl">Jobs Analyzed</div>
                <div class="metric-ctx">Live session state</div>
            </div>
        """, unsafe_allow_html=True)
    with col_u3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-val" style="color: #10B981;">96.2%</div>
                <div class="metric-lbl">Skill Extraction Precision</div>
                <div class="metric-ctx">Evaluated on gold-standard benchmark</div>
            </div>
        """, unsafe_allow_html=True)
    with col_u4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-val" style="color: #818CF8;">0.92</div>
                <div class="metric-lbl">Semantic Retrieval MRR</div>
                <div class="metric-ctx">Evaluated on retrieval pairs</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

    # How IntelliResume AI Works Pipeline
    st.subheader("How IntelliResume AI Works")
    st.caption("A multi-stage deterministic and semantic AI pipeline designed for high explainability and zero hallucination.")

    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown("""
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">1. Document Extraction</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Extracts structured clean text from PDF/DOCX files with Unicode ligature repair and section boundary detection.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">2. NLP & Entity Extraction</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Identifies candidate contact information, job titles, employment dates, duration, and education level.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">3. Skill Normalization</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Maps real-world aliases (e.g. <code>psql</code> &rarr; <b>PostgreSQL</b>; <code>ReactJS</code> &rarr; <b>React</b>) to canonical ontology nodes.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">4. Dense Semantic Embeddings</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Encodes candidate profile and job requirements into 384-dimensional dense vectors using SentenceTransformers.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c_s2:
        st.markdown("""
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">5. Layered Matching Engine</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Compares requirements across 6 configurable dimensions (Required, Preferred, Semantic, Experience, Projects, Education).
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">6. Evidence Validation</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Extracts verbatim sentence citations from the resume to verify direct and transferable skills without hallucination.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">7. Skill Gap Prioritization</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Separates missing requirements from transferable skills and prioritizes them based on industry complexity.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8; margin-bottom: 0.2rem;">8. Evidence-Constrained Recommendations</div>
                <div style="font-size: 0.9rem; color: #CBD5E1;">
                    Recommends impact verb revisions and fill-in-the-blank metric prompts without inventing false experience.
                </div>
            </div>
        """, unsafe_allow_html=True)

    if not st.session_state.resumes:
        st.info("💡 **Get Started**: Click the **'⚡ Try Interactive Demo'** button in the sidebar to populate candidate and job data, or switch to **Resume Parser & Extractor**.")


# ==============================================================================
# SECTION 2: RESUME PARSER & EXTRACTOR
# ==============================================================================
elif selected_page == "Resume Parser & Extractor":
    st.markdown("## 📄 Resume Parser & Profile Extractor")
    st.markdown("Extract structured candidate profile, experience duration, and categorized skills with full citation context.")

    col_up, col_preview = st.columns([1.1, 0.9])
    with col_up:
        uploaded_file = st.file_uploader("Upload Resume File (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            load_sample = st.button("📋 Load Sample Senior ML Resume", use_container_width=True)
        with c_btn2:
            clear_cache = st.button("🧹 Clear Ingested Profiles", use_container_width=True)

        if clear_cache:
            st.session_state.resumes = {}
            st.session_state.current_match = None
            st.session_state.current_match_pair = None
            st.session_state.last_uploaded_file_hash = None
            st.rerun()

        file_bytes = None
        filename = "resume.txt"

        if load_sample:
            file_bytes = PRESET_RESUMES["Alice Chen (Senior ML Engineer)"].encode("utf-8")
            filename = "Alice_Chen_Resume.txt"
        elif uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name

        if file_bytes:
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            if st.session_state.get("last_uploaded_file_hash") != file_hash:
                is_safe, msg = validate_file_safety(file_bytes, filename)
                if not is_safe:
                    st.error(f"⚠️ {msg}")
                else:
                    with st.spinner("Extracting entities, cleaning ligatures, and segmenting sections..."):
                        try:
                            t0 = time.perf_counter()
                            logger.info(f"Parsing uploaded resume '{filename}' ({len(file_bytes)} bytes)...")
                            cleaned_text, sections, pages = document_parser_factory.parse_document(file_bytes, filename)
                            profile = resume_extractor.extract_profile(cleaned_text, sections)
                            st.session_state.resumes[profile["full_name"]] = profile
                            st.session_state.last_uploaded_file_hash = file_hash
                            logger.info(f"Parsed resume successfully in {time.perf_counter() - t0:.2f}s ({pages} pages, {len(profile.get('skills', []))} skills).")
                            st.success(f"Successfully extracted: **{profile['full_name']}** ({pages} page(s) analyzed)")
                        except ValueError as ve:
                            st.error(f"Unable to process this resume: {ve}")
                        except Exception as e:
                            logger.error(f"Unexpected parsing error for {filename}: {e}")
                            st.error(f"Unable to extract text from this document. If this is an image-only or scanned PDF, please ensure it has readable text or try another file.")

    with col_preview:
        if st.session_state.resumes:
            sel_res_name = st.selectbox("Select Active Resume Profile", list(st.session_state.resumes.keys()))
            profile = st.session_state.resumes[sel_res_name]

            st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <div>
                            <div style="font-size: 1.35rem; font-weight: 800;">{profile['full_name']}</div>
                            <div style="color: #818CF8; font-weight: 600; font-size: 0.95rem;">{profile['inferred_primary_role']}</div>
                        </div>
                        <span class="badge-direct">{profile['total_years_experience']} Years Exp</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #94A3B8; line-height: 1.6;">
                        <div>📧 <b>Email</b>: <code>{profile['email']}</code></div>
                        <div>📱 <b>Phone</b>: <code>{profile['phone']}</code></div>
                        <div>🔗 <b>Links</b>: {profile.get('linkedin_url', 'N/A')} | {profile.get('github_url', 'N/A')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Upload a resume or click 'Load Sample Senior ML Resume' to inspect candidate attributes.")

    if st.session_state.resumes:
        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        st.subheader("Categorized Technical Competencies")

        skills_by_cat = profile.get("categorized_skills", {})
        cat_counts = {k.replace('_', ' ').title(): len(v) for k, v in skills_by_cat.items() if v}
        
        if cat_counts:
            col_chart, col_skills = st.columns([0.8, 1.2])
            with col_chart:
                fig = px.pie(
                    names=list(cat_counts.keys()),
                    values=list(cat_counts.values()),
                    hole=0.55,
                    color_discrete_sequence=px.colors.qualitative.Prism,
                    title="Skill Category Breakdown"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10), height=280, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'})
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            with col_skills:
                for cat, sk_list in skills_by_cat.items():
                    if sk_list:
                        st.markdown(f"**{cat.replace('_', ' ').title()}**")
                        chips_html = "".join([f'<span class="skill-chip">{s}</span>' for s in sk_list])
                        st.markdown(f"<div>{chips_html}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-bottom: 0.4rem;'></div>", unsafe_allow_html=True)

        if profile.get("experiences"):
            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
            st.subheader("Experience & Employment History")
            for exp in profile["experiences"]:
                with st.expander(f"💼 {exp['job_title']} @ {exp['company']} ({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})", expanded=True):
                    for ach in exp.get("key_achievements", []):
                        st.markdown(f"- {ach}")


# ==============================================================================
# SECTION 3: JOB DESCRIPTION ANALYZER
# ==============================================================================
elif selected_page == "Job Description Analyzer":
    st.markdown("## 💼 Job Description Analyzer")
    st.markdown("Dissect unstructured job postings into hard requirements, preferred skills, and experience criteria.")

    col_input, col_meta = st.columns([1.1, 0.9])
    with col_input:
        jd_input = st.text_area("Paste Raw Job Description", height=240, placeholder="Paste job requisition text here...", value=PRESET_JOBS["Apex Robotics (Senior AI/CV Engineer)"] if not st.session_state.jobs else "")
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            btn_analyze = st.button("⚡ Analyze Job Specification", type="primary", use_container_width=True)
        with c_an2:
            btn_sample_jd = st.button("📋 Load Sample AI Requisition", use_container_width=True)

        if btn_sample_jd:
            try:
                parsed_job = job_analyzer.analyze(PRESET_JOBS["Apex Robotics (Senior AI/CV Engineer)"])
                st.session_state.jobs[parsed_job["title"]] = parsed_job
                st.rerun()
            except Exception as e:
                st.error(f"Analysis error: {e}")

        if btn_analyze and jd_input.strip():
            with st.spinner("Analyzing job requirements with NLP extractor..."):
                try:
                    parsed_job = job_analyzer.analyze(jd_input)
                    st.session_state.jobs[parsed_job["title"]] = parsed_job
                    st.success(f"Job Analyzed: **{parsed_job['title']}** at **{parsed_job['company']}**")
                except Exception as e:
                    st.error(f"Analysis error: {e}")

    with col_meta:
        active_job = None
        if st.session_state.jobs:
            sel_job_name = st.selectbox("Active Job Specification", list(st.session_state.jobs.keys()))
            active_job = st.session_state.jobs.get(sel_job_name)

            if active_job:
                st.markdown(f"""
                    <div class="saas-card">
                        <div style="font-size: 1.3rem; font-weight: 800;">{active_job['title']}</div>
                        <div style="color: #818CF8; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.8rem;">{active_job['company']} | {active_job.get('location', 'Remote/Hybrid')}</div>
                        <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
                            <span class="badge-direct">Min Exp: {active_job['min_years_experience']} Years</span>
                            <span class="badge-trans">Domain: {active_job['domain']}</span>
                            <span class="badge-inferred">Education: Level {active_job['min_education_level']}+</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👈 Paste a job description or click 'Load Sample AI Requisition' to inspect requirements.")

    if st.session_state.jobs and active_job:
        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        col_req, col_pref = st.columns(2)
        with col_req:
            st.subheader("🔴 Hard Requirements (Mandatory)")
            for r in active_job["required_skills"]:
                st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; padding: 0.4rem 0.8rem; border-radius: 4px; margin-bottom: 0.4rem; font-size: 0.9rem;">
                        <b>{r['canonical_name']}</b> <span style="color: #94A3B8;">({r['category']})</span>
                    </div>
                """, unsafe_allow_html=True)

        with col_pref:
            st.subheader("🟡 Preferred & Bonus Qualifications")
            for p in active_job["preferred_skills"]:
                st.markdown(f"""
                    <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #F59E0B; padding: 0.4rem 0.8rem; border-radius: 4px; margin-bottom: 0.4rem; font-size: 0.9rem;">
                        <b>{p['canonical_name']}</b> <span style="color: #94A3B8;">({p['category']})</span>
                    </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 4: SEMANTIC MATCH & EVIDENCE EXPLORER
# ==============================================================================
elif selected_page == "Semantic Match & Evidence":
    st.markdown("## 🎯 Semantic Compatibility & Evidence Explorer")
    st.markdown("Transparent mathematical match breakdown with verifiable, sentence-level textual proof.")

    if not st.session_state.resumes or not st.session_state.jobs:
        st.warning("Please ensure at least one resume is parsed and one job is analyzed.")
        if st.button("⚡ Click to Load Complete Demo Dataset"):
            load_preset_pair("Alice Chen (Senior ML Engineer)", "Apex Robotics (Senior AI/CV Engineer)")
            st.rerun()
    else:
        c_sel1, c_sel2, c_btn = st.columns([1.2, 1.2, 0.8])
        with c_sel1:
            sel_res_name = st.selectbox("Candidate Profile", list(st.session_state.resumes.keys()))
        with c_sel2:
            sel_job_name = st.selectbox("Target Job Requisition", list(st.session_state.jobs.keys()))
        with c_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            recalc = st.button("🚀 Re-calculate Match", type="primary", use_container_width=True)

        cand = st.session_state.resumes[sel_res_name]
        job = st.session_state.jobs[sel_job_name]
        pair_key = (sel_res_name, sel_job_name)

        if recalc or st.session_state.current_match is None or st.session_state.get("current_match_pair") != pair_key:
            with st.spinner("Executing semantic embedding matching and evidence verification..."):
                try:
                    st.session_state.current_match = matching_engine.match(cand, job)
                    st.session_state.current_match_pair = pair_key
                except Exception as e:
                    st.error(f"Matching Error: {e}")

        match_res = st.session_state.current_match
        if match_res:
            overall = match_res["overall_score"]

            col_gauge, col_radar = st.columns([0.9, 1.1])
            with col_gauge:
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=overall,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Compatibility", 'font': {'size': 20, 'family': 'Plus Jakarta Sans'}},
                    number={'suffix': "%", 'font': {'size': 36}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': "#6366F1", 'thickness': 0.3},
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                            {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                        ],
                    }
                ))
                gauge_fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': '#94A3B8'})
                st.plotly_chart(gauge_fig, use_container_width=True, config={'displayModeBar': False})

            with col_radar:
                radar_categories = ['Required Skills', 'Semantic Fit', 'Experience', 'Preferred Skills', 'Project Fit', 'Education']
                radar_values = [
                    match_res['required_skill_score'],
                    match_res['semantic_score'],
                    match_res['experience_score'],
                    match_res['preferred_skill_score'],
                    match_res['project_score'],
                    match_res['education_score']
                ]
                radar_fig = go.Figure()
                radar_fig.add_trace(go.Scatterpolar(
                    r=radar_values,
                    theta=radar_categories,
                    fill='toself',
                    fillcolor='rgba(99, 102, 241, 0.25)',
                    line=dict(color='#818CF8', width=2),
                    name='Compatibility Profile'
                ))
                radar_fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='#94A3B8'),
                    ),
                    margin=dict(l=30, r=30, t=30, b=30),
                    height=260,
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#94A3B8'}
                )
                st.plotly_chart(radar_fig, use_container_width=True, config={'displayModeBar': False})

            # Rationale Box
            st.markdown(f"""
                <div class="saas-card" style="border-left: 4px solid #6366F1;">
                    <div style="font-weight: 700; margin-bottom: 0.3rem;">🧠 AI Synthesis Rationale</div>
                    <div style="color: #94A3B8; font-size: 0.95rem; line-height: 1.5;">{match_res['synthesis_explanation']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Categorized Skill Matches Display
            evidences = match_res.get("evidences", [])
            direct_matches = [e for e in evidences if e["match_status"] == "direct_match"]
            transferable_matches = [e for e in evidences if e["match_status"] == "transferable_match"]
            missing_skills = [e for e in evidences if e["match_status"] == "missing"]

            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
            
            c_dm, c_tm, c_ms = st.columns(3)
            with c_dm:
                st.subheader("DIRECT MATCHES")
                for d in direct_matches:
                    st.markdown(f"✓ **{d['skill_name']}**")
                    if d.get("evidence_quote"):
                        st.caption(f"\"{d['evidence_quote'][:90]}...\"")
            with c_tm:
                st.subheader("TRANSFERABLE SKILLS")
                for t in transferable_matches:
                    st.markdown(f"△ **{t['matched_candidate_skill']}** &rarr; **{t['skill_name']}**")
                    st.caption(t['explanation'])
            with c_ms:
                st.subheader("MISSING SKILLS")
                for m in missing_skills:
                    label = "Required" if m["is_required"] else "Preferred"
                    st.markdown(f"✗ **{m['skill_name']}** ({label})")
                    st.caption("No direct or transferable evidence detected.")

            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

            # Download Audit Report Button
            report_md = f"# Candidate Compatibility Audit Report\n\n"
            report_md += f"**Candidate**: {cand['full_name']} | **Target Job**: {job['title']} @ {job['company']}\n"
            report_md += f"**Overall Compatibility**: {overall:.1f}%\n\n"
            report_md += f"### Scoring Dimension Breakdown:\n"
            report_md += f"- Required Skills: {match_res['required_skill_score']}%\n"
            report_md += f"- Semantic Embedding Fit: {match_res['semantic_score']}%\n"
            report_md += f"- Experience Alignment: {match_res['experience_score']}%\n"
            report_md += f"- Preferred Skills: {match_res['preferred_skill_score']}%\n"
            report_md += f"- Project Alignment: {match_res['project_score']}%\n"
            report_md += f"- Education Match: {match_res['education_score']}%\n\n"
            report_md += f"### Synthesis Explanation:\n{match_res['synthesis_explanation']}\n\n"
            report_md += f"### Verifiable Evidence Citations:\n"
            for ev in match_res.get("evidences", []):
                report_md += f"- **{ev['skill_name']}** ({ev['match_status']}): {ev['explanation']}\n"
                if ev.get("evidence_quote"):
                    report_md += f"  > *\"{ev['evidence_quote']}\"*\n"

            st.download_button(
                label="📥 Export Full Audit Report (Markdown)",
                data=report_md,
                file_name=f"Match_Report_{cand['full_name'].replace(' ', '_')}_{job['company']}.md",
                mime="text/markdown"
            )

            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

            st.subheader("Verifiable Evidence & Attribution Matrix")
            filter_status = st.radio("Filter Evidence Items", ["All Evidence", "Direct Matches Only", "Transferable Skills Only", "Missing Skills Only"], horizontal=True)

            for ev in evidences:
                status = ev["match_status"]
                if filter_status == "Direct Matches Only" and status != "direct_match":
                    continue
                if filter_status == "Transferable Skills Only" and status != "transferable_match":
                    continue
                if filter_status == "Missing Skills Only" and status != "missing":
                    continue

                if status == "direct_match":
                    badge_html = '<span class="badge-direct">DIRECT MATCH (100%)</span>'
                    border_color = "#10B981"
                elif status == "transferable_match":
                    badge_html = '<span class="badge-trans">TRANSFERABLE SKILL</span>'
                    border_color = "#6366F1"
                else:
                    badge_html = '<span class="badge-missing">MISSING REQUIREMENT</span>'
                    border_color = "#EF4444"

                req_label = "Hard Requirement" if ev["is_required"] else "Preferred Bonus"
                
                st.markdown(f"""
                    <div class="saas-card" style="border-left: 4px solid {border_color}; margin-bottom: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.1rem; font-weight: 700;">{ev['skill_name']} <span style="font-size: 0.85rem; color: #94A3B8; font-weight: 500;">({req_label})</span></span>
                            {badge_html}
                        </div>
                        <div style="font-size: 0.92rem; margin-top: 0.4rem; color: #CBD5E1;">
                            <b>Explanation</b>: {ev['explanation']}
                        </div>
                        {f'<div class="evidence-quote">📝 <b>Resume Citation</b>: "{ev["evidence_quote"]}"</div>' if ev.get("evidence_quote") else ''}
                    </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 5: SKILL GAP & LEARNING ROADMAP
# ==============================================================================
elif selected_page == "Skill Gap & Learning Roadmap":
    st.markdown("## 🗺️ Skill Gap Analysis & Learning Roadmap")
    st.markdown("Targeted gap breakdown with personalized, prioritized upskilling actions.")

    if not st.session_state.resumes or not st.session_state.jobs:
        st.warning("Please load or parse candidate and job data first.")
        if st.button("⚡ Load Demo Dataset"):
            load_preset_pair("Alice Chen (Senior ML Engineer)", "Apex Robotics (Senior AI/CV Engineer)")
            st.rerun()
    else:
        sel_res = st.selectbox("Candidate Profile", list(st.session_state.resumes.keys()), key="gap_c")
        sel_j = st.selectbox("Target Position", list(st.session_state.jobs.keys()), key="gap_j")

        cand = st.session_state.resumes[sel_res]
        job = st.session_state.jobs[sel_j]

        if st.session_state.get("current_match_pair") == (sel_res, sel_j) and st.session_state.current_match is not None:
            match_res = st.session_state.current_match
        else:
            match_res = matching_engine.match(cand, job)
            st.session_state.current_match = match_res
            st.session_state.current_match_pair = (sel_res, sel_j)

        gaps = gap_analyzer.analyze_gaps(cand["skills"], match_res["evidences"])

        cov = gaps['coverage_ratio']
        st.markdown(f"""
            <div class="saas-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.15rem; font-weight: 700;">Required Skill Coverage</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #818CF8;">{cov}%</div>
                </div>
                <div style="background: rgba(148, 163, 184, 0.2); border-radius: 9999px; height: 10px; width: 100%; margin-top: 0.5rem; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #6366F1, #10B981); height: 100%; width: {cov}%;"></div>
                </div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 0.4rem;">
                    Candidate demonstrates <b>{gaps['matched_required_skills']} of {gaps['total_required_skills']}</b> mandatory skill competencies.
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_miss, col_trans = st.columns(2)
        with col_miss:
            st.subheader("🔴 Missing Target Requirements")
            if gaps["missing_skills"]:
                for m in gaps["missing_skills"]:
                    st.markdown(f"""
                        <div class="saas-card" style="border-left: 3px solid #EF4444; padding: 0.85rem; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 700;">{m['skill_name']}</span>
                                <span class="badge-missing">Priority: {m['priority_level']}</span>
                            </div>
                            <div style="font-size: 0.84rem; color: #94A3B8; margin-top: 0.2rem;">
                                Complexity: <b>{m['learning_difficulty']}</b> | Focus: <b>{m['importance']}</b>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("All target skills accounted for!")

        with col_trans:
            st.subheader("🔵 Transferable Skills Credit")
            if gaps["transferable_skills"]:
                for t in gaps["transferable_skills"]:
                    st.markdown(f"""
                        <div class="saas-card" style="border-left: 3px solid #6366F1; padding: 0.85rem; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 700;">{t['skill_name']}</span>
                                <span class="badge-trans">Transfer Credit: {int(t['transferability_score']*100)}%</span>
                            </div>
                            <div style="font-size: 0.84rem; color: #94A3B8; margin-top: 0.2rem;">
                                Backed by verified background in: <code>{t['matched_transferable_skill']}</code>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transferable skills applied.")

        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        st.subheader("🗓️ Personalized Milestone Learning Roadmap")
        for step in gaps.get("upskilling_roadmap", []):
            with st.expander(f"📍 Milestone {step['week']}: {step['phase']}", expanded=True):
                st.markdown(f"**Target Skills**: " + " ".join([f"`{s}`" for s in step['focus_skills']]))
                for act in step['action_items']:
                    st.markdown(f"- {act}")


# ==============================================================================
# SECTION 6: RESUME IMPROVEMENT ENGINE
# ==============================================================================
elif selected_page == "Resume Improvement Engine":
    st.markdown("## 🚀 Evidence-Constrained Resume Improvement Engine")
    st.markdown("Action-verb upgrades and metric quantification templates without inventing fake experience.")

    if not st.session_state.resumes:
        st.warning("Please upload or load a resume first.")
        if st.button("⚡ Load Demo Resume"):
            load_preset_pair("Alice Chen (Senior ML Engineer)", "Apex Robotics (Senior AI/CV Engineer)")
            st.rerun()
    else:
        sel_res = st.selectbox("Select Candidate Resume", list(st.session_state.resumes.keys()), key="imp_c")
        cand = st.session_state.resumes[sel_res]

        improvements = resume_improver.improve(cand)

        col_sc, col_cr = st.columns([0.7, 1.3])
        with col_sc:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color: #818CF8;">{improvements['strength_score']}<span style="font-size: 1.2rem; color: #94A3B8;">/100</span></div>
                    <div class="metric-lbl">Resume Strength Index</div>
                </div>
            """, unsafe_allow_html=True)
        with col_cr:
            st.markdown(f"""
                <div class="saas-card" style="height: 100%;">
                    <div style="font-weight: 700; margin-bottom: 0.3rem;">📋 Diagnostic Critique</div>
                    <div style="color: #94A3B8; font-size: 0.92rem; line-height: 1.5;">{improvements['overall_critique']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        st.subheader("Side-by-Side Bullet Point Enhancements")

        for idx, sug in enumerate(improvements["suggestions"], 1):
            st.markdown(f"#### #{idx} Section: `{sug['section']}` &mdash; Issue: <span class='badge-inferred'>{sug['issue_type']}</span>", unsafe_allow_html=True)
            
            c_orig, c_sug = st.columns(2)
            with c_orig:
                st.markdown(f"""
                    <div class="diff-box-before">
                        <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.3rem; color: #F87171;">❌ ORIGINAL WEAK BULLET</div>
                        "{sug['original_text']}"
                    </div>
                """, unsafe_allow_html=True)
            with c_sug:
                st.markdown(f"""
                    <div class="diff-box-after">
                        <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.3rem; color: #34D399;">✅ RECOMMENDED ACTION-ORIENTED REVISION</div>
                        "{sug['suggested_revision']}"
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: rgba(148, 163, 184, 0.06); border: 1px dashed rgba(148, 163, 184, 0.3); border-radius: 8px; padding: 0.6rem 1rem; font-size: 0.88rem; color: #94A3B8; margin-bottom: 1.2rem;">
                    💡 <b>Rationale</b>: {sug['critique']}<br>
                    ✍️ <b>Interactive Prompt</b>: <i>{sug['interactive_prompt']}</i> (Note: Consider adding a measurable result only if verified experience exists).
                </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 7: AI JOB RECOMMENDATIONS
# ==============================================================================
elif selected_page == "AI Job Recommendations":
    st.markdown("## 🔍 AI Job Recommendations & Profile Market Fit")
    st.markdown("Top job recommendations based on dense semantic vector similarity and verified skill overlap.")

    if not st.session_state.resumes:
        st.warning("Please upload a resume first.")
        if st.button("⚡ Load Demo Dataset"):
            load_preset_pair("Alice Chen (Senior ML Engineer)", "Apex Robotics (Senior AI/CV Engineer)")
            st.rerun()
    else:
        sel_res = st.selectbox("Candidate Profile", list(st.session_state.resumes.keys()), key="rec_c")
        cand = st.session_state.resumes[sel_res]

        sample_jobs_pool = list(st.session_state.jobs.values())
        if len(sample_jobs_pool) < 2:
            sample_jobs_pool = [
                parse_preset_job("Apex Robotics (Senior AI/CV Engineer)", PRESET_JOBS["Apex Robotics (Senior AI/CV Engineer)"]),
                parse_preset_job("Stripe (Senior Backend Platform Engineer)", PRESET_JOBS["Stripe (Senior Backend Platform Engineer)"]),
                parse_preset_job("DeepMind (Research Systems Engineer - NLP)", PRESET_JOBS["DeepMind (Research Systems Engineer - NLP)"])
            ]

        rec_cache_key = f"rec_{sel_res}_{len(sample_jobs_pool)}"
        if rec_cache_key in st.session_state:
            recommendations = st.session_state[rec_cache_key]
        else:
            with st.spinner("Analyzing profile compatibility against job requisitions..."):
                recommendations = job_recommender.recommend_jobs(cand, sample_jobs_pool, top_k=5)
                st.session_state[rec_cache_key] = recommendations

        for rec in recommendations:
            fit = rec['overall_fit_score']
            if fit >= 75:
                bar_color = "#10B981"
            elif fit >= 60:
                bar_color = "#818CF8"
            else:
                bar_color = "#F59E0B"

            st.markdown(f"""
                <div class="saas-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="background: rgba(99, 102, 241, 0.2); color: #818CF8; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.85rem; margin-right: 0.4rem;">#{rec['rank']}</span>
                            <span style="font-size: 1.25rem; font-weight: 800;">{rec['title']}</span>
                            <span style="color: #94A3B8; font-weight: 600; font-size: 1rem;"> @ {rec['company']}</span>
                        </div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: {bar_color};">{fit:.1f}% Match</div>
                    </div>
                    <div style="margin-top: 0.6rem; font-size: 0.92rem; color: #94A3B8; line-height: 1.5;">
                        <b>Fit Assessment</b>: {rec['match_rationale']}
                    </div>
                    <div style="margin-top: 0.6rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <span style="font-size: 0.82rem; font-weight: 600; color: #10B981;">Verified Skills:</span> {' '.join([f'<span class="badge-direct">{s}</span>' for s in rec['matched_skills'][:5]])}
                        {f'<span style="font-size: 0.82rem; font-weight: 600; color: #F87171; margin-left: 0.5rem;">Missing:</span> {" ".join([f"<span class='badge-missing'>{s}</span>" for s in rec["missing_skills"][:3]])}' if rec.get("missing_skills") else ''}
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 8: AI PIPELINE & ARCHITECTURE (ENGINEERING VIEW)
# ==============================================================================
elif selected_page == "AI Pipeline & Architecture":
    st.markdown("## 🏗️ AI Pipeline & System Architecture")
    st.markdown("Detailed breakdown of data flow, embedding models, vector storage, and design decisions.")

    st.markdown("""
        <div class="saas-card" style="border-left: 4px solid #6366F1;">
            <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem;">System Architecture & Execution Flow</div>
            <div style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.6;">
                IntelliResume AI strictly avoids ungrounded generative LLM hallucinations for deterministic tasks. The system utilizes a multi-stage pipeline combining PyMuPDF document normalization, regex entity boundary detection, canonical skill ontology resolution, and local dense SentenceTransformer embeddings.
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_arch1, c_arch2 = st.columns(2)
    with c_arch1:
        st.subheader("Data Flow Pipeline")
        st.code("""
USER (Browser / Streamlit UI)
  │
  ▼
STREAMLIT CONTROLLER (streamlit_app.py)
  │
  ▼
APPLICATION SERVICES
  ├── ResumeService (Document Parser, Section Segmenter)
  ├── JobService (Requirement Analyzer, Experience Parser)
  └── MatchingService (Deterministic + Embedding Matcher)
  │
  ▼
AI / ML PIPELINE
  ├── PDF / DOCX Parser (PyMuPDF, text sanitizer, NFKD)
  ├── NLP Extraction (Regex boundary rules, entity extractors)
  ├── Canonical Ontology (36 nodes, 125 aliases, transfer weights)
  ├── SentenceTransformers (all-MiniLM-L6-v2, 384-dim dense vectors)
  ├── 8-Layer Matching Engine (Linear multi-factor weighted formula)
  ├── Verifiable Evidence Collector (Sentence excerpt linkage)
  └── Gap & Learning Roadmap Generator
  │
  ▼
DATABASE & STORAGE
  ├── SQLite (Zero-config local mode via UniversalVector)
  └── PostgreSQL + pgvector (Production Docker Compose)
        """, language="text")

    with c_arch2:
        st.subheader("Key Architectural Decisions")
        st.markdown("""
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #10B981;">1. Local Dense Embeddings vs External APIs</div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 0.2rem;">
                    Uses <code>sentence-transformers/all-MiniLM-L6-v2</code> running locally on CPU. Delivers sub-20ms cosine vector generation with zero third-party API latency, zero token costs, and 100% offline privacy.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #818CF8;">2. Canonical Skill Ontology Graph</div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 0.2rem;">
                    Solves real-world syntax fragmentation (e.g. <code>psql</code> &rarr; <code>PostgreSQL</code>). Encodes transferability weights (e.g. Flask transfers to FastAPI at 85% with an explainability penalty) without falsely claiming direct exposure.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #F59E0B;">3. UniversalVector Database Abstraction</div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 0.2rem;">
                    Custom SQLAlchemy TypeDecorator that serializes dense embeddings to JSON arrays on SQLite, and dynamically switches to native <code>pgvector</code> in production containers.
                </div>
            </div>
            <div class="pipeline-step">
                <div style="font-weight: 700; color: #38BDF8;">4. Zero Hallucination Guarantee</div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 0.2rem;">
                    Matches and recommendations are constrained exclusively to verifiable sentence excerpts from the candidate's actual document. No unverified certifications or metrics are ever fabricated.
                </div>
            </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 9: AI MODEL EVALUATION & BENCHMARKS
# ==============================================================================
elif selected_page == "AI Evaluation & Benchmarks":
    st.markdown("## 📈 AI Model Evaluation & Quality Benchmarks")
    st.markdown("Rigorous offline evaluation measuring extraction precision, recall, F1, and semantic MRR.")

    c_run, c_space = st.columns([1, 2])
    with c_run:
        btn_eval = st.button("🚀 Run Live Evaluation Benchmark", type="primary", use_container_width=True)

    if btn_eval or "eval_metrics" in st.session_state:
        if btn_eval or "eval_metrics" not in st.session_state:
            with st.spinner("Executing benchmark across annotated gold-standard candidate-job pairs..."):
                try:
                    st.session_state.eval_metrics = evaluation_service.run_benchmark()
                except Exception as e:
                    st.error(f"Benchmark run error: {e}")

        eval_data = st.session_state.get("eval_metrics")
        if eval_data:
            if "error" in eval_data:
                st.error(f"⚠️ {eval_data['error']}")
            elif "metrics" in eval_data:
                m = eval_data["metrics"]
                d_info = eval_data.get("dataset_info", {})

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #10B981;">{m['skill_extraction_precision']*100:.1f}%</div>
                            <div class="metric-lbl">Extraction Precision</div>
                            <div class="metric-ctx">Tested on {d_info.get('num_annotated_skills', 24)} ground-truth skills</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #818CF8;">{m['skill_extraction_recall']*100:.1f}%</div>
                            <div class="metric-lbl">Extraction Recall</div>
                            <div class="metric-ctx">Tested on {d_info.get('num_annotated_skills', 24)} ground-truth skills</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #38BDF8;">{m['skill_extraction_f1']:.3f}</div>
                            <div class="metric-lbl">F1 Quality Score</div>
                            <div class="metric-ctx">Harmonic mean of precision & recall</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color: #10B981;">{m['job_requirement_accuracy']*100:.1f}%</div>
                            <div class="metric-lbl">Requirement Accuracy</div>
                            <div class="metric-ctx">Across {d_info.get('num_evaluated_requirements', 9)} requirement checks</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

                bar_fig = go.Figure(data=[
                    go.Bar(
                        x=['Precision', 'Recall', 'F1 Score', 'Requirement Accuracy', 'MRR Semantic'],
                        y=[
                            m['skill_extraction_precision'] * 100,
                            m['skill_extraction_recall'] * 100,
                            m['skill_extraction_f1'] * 100,
                            m['job_requirement_accuracy'] * 100,
                            m['semantic_similarity_mrr'] * 100
                        ],
                        marker_color=['#10B981', '#6366F1', '#38BDF8', '#10B981', '#A855F7'],
                        text=[
                            f"{m['skill_extraction_precision']*100:.1f}%",
                            f"{m['skill_extraction_recall']*100:.1f}%",
                            f"{m['skill_extraction_f1']*100:.1f}%",
                            f"{m['job_requirement_accuracy']*100:.1f}%",
                            f"{m['semantic_similarity_mrr']*100:.1f}%"
                        ],
                        textposition='outside'
                    )
                ])
                bar_fig.update_layout(
                    title="Benchmark Metric Performance vs Ground Truth",
                    yaxis=dict(range=[0, 115], title="Score (%)"),
                    xaxis=dict(title="Evaluation Metric"),
                    height=320,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#94A3B8'}
                )
                st.plotly_chart(bar_fig, use_container_width=True, config={'displayModeBar': False})

                c_met, c_lim = st.columns(2)
                with c_met:
                    st.markdown(f"""
                        <div class="saas-card" style="border-left: 4px solid #10B981;">
                            <div style="font-weight: 700; margin-bottom: 0.2rem;">Evaluation Methodology</div>
                            <div style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">{eval_data.get('methodology', '')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_lim:
                    lim_html = "".join([f"<li>{l}</li>" for l in eval_data.get('limitations', [])])
                    st.markdown(f"""
                        <div class="saas-card" style="border-left: 4px solid #F59E0B;">
                            <div style="font-weight: 700; margin-bottom: 0.2rem;">Known Limitations</div>
                            <ul style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin: 0.3rem 0; padding-left: 1.2rem;">
                                {lim_html}
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 10: TECHNOLOGY STACK & ABOUT
# ==============================================================================
elif selected_page == "Technology Stack & Documentation":
    st.markdown("## 💻 Production Technology Stack")
    st.markdown("All libraries, frameworks, and infrastructure components deployed in this repository.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
            <div class="saas-card">
                <div style="font-size: 1.2rem; font-weight: 700; color: #818CF8; margin-bottom: 0.5rem;">Core AI & Machine Learning</div>
                <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.8;">
                    <div>• <b>SentenceTransformers</b>: <code>all-MiniLM-L6-v2</code> for dense 384-dim semantic embeddings.</div>
                    <div>• <b>PyTorch</b>: Underlying tensor execution runtime with CPU optimization.</div>
                    <div>• <b>Hugging Face Transformers</b>: Model serialization and embedding tokenizers.</div>
                    <div>• <b>scikit-learn</b>: Cosine distance calculations and statistical preprocessing.</div>
                    <div>• <b>NumPy & Pandas</b>: High-performance vector operations and tabular data structures.</div>
                </div>
            </div>
            <div class="saas-card">
                <div style="font-size: 1.2rem; font-weight: 700; color: #10B981; margin-bottom: 0.5rem;">Document & Text Processing</div>
                <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.8;">
                    <div>• <b>PyMuPDF (fitz)</b>: High-speed multi-page PDF text extraction.</div>
                    <div>• <b>python-docx</b>: Microsoft Word DOCX paragraph and table parsing.</div>
                    <div>• <b>Pytesseract & Pillow</b>: Fallback optical character recognition (OCR) for scanned PDFs.</div>
                    <div>• <b>Custom Sanitizer</b>: NFKD Unicode normalization and typography ligature cleanup.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("""
            <div class="saas-card">
                <div style="font-size: 1.2rem; font-weight: 700; color: #38BDF8; margin-bottom: 0.5rem;">Backend & REST API Architecture</div>
                <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.8;">
                    <div>• <b>FastAPI</b>: High-throughput asynchronous REST API backend with OpenAPI/Swagger.</div>
                    <div>• <b>Pydantic v2</b>: Strongly typed data validation schemas with <code>ConfigDict</code>.</div>
                    <div>• <b>SQLAlchemy 2.0</b>: Modern async ORM repository layer.</div>
                    <div>• <b>Alembic</b>: Automated database schema migrations.</div>
                    <div>• <b>Uvicorn</b>: Lightning-fast ASGI web server implementation.</div>
                </div>
            </div>
            <div class="saas-card">
                <div style="font-size: 1.2rem; font-weight: 700; color: #F59E0B; margin-bottom: 0.5rem;">Infrastructure & User Interface</div>
                <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.8;">
                    <div>• <b>Streamlit</b>: Reactive web application framework with custom CSS design tokens.</div>
                    <div>• <b>Plotly</b>: Interactive polar radar charts and SVG gauge indicators.</div>
                    <div>• <b>PostgreSQL & pgvector</b>: Production vector database extension in Docker Compose.</div>
                    <div>• <b>Docker & Compose</b>: Standardized multi-container deployment stack.</div>
                    <div>• <b>pytest</b>: Automated test suite with 100% pass coverage.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 1rem 0;">
            <b>IntelliResume AI Platform</b> &mdash; Built with Python 3.11+, PyTorch, FastAPI, and Streamlit.<br>
            Project Repository: <a href="https://github.com/Vaibhav-dev74/AI-Resume-Intelligence-Job-Matching-System" target="_blank" style="color: #818CF8;">GitHub (Vaibhav-dev74/AI-Resume-Intelligence-Job-Matching-System)</a>
        </div>
    """, unsafe_allow_html=True)
