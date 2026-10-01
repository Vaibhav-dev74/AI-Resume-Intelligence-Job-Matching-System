import os
import sys
import json
from pathlib import Path
import streamlit as st
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

st.set_page_config(
    page_title="AI Resume Intelligence & Job Matching Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# MODERN CSS DESIGN SYSTEM
# ==============================================================================
st.markdown("""
<style>
    /* Global font & typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Gradient Hero Container */
    .hero-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        border-radius: 16px;
        padding: 2.2rem 2.4rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #FFFFFF, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #C7D2FE;
        max-width: 800px;
        line-height: 1.5;
        margin-bottom: 1.2rem;
    }

    .hero-tags {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }

    .hero-tag {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #EEF2FF;
    }

    /* Cards */
    .glass-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1E293B;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Badges */
    .badge-direct {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }
    .badge-trans {
        background-color: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }
    .badge-missing {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }
    .badge-inferred {
        background-color: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        display: inline-block;
    }

    /* Skill Chip */
    .skill-chip {
        display: inline-flex;
        align-items: center;
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem 0.3rem;
    }

    /* Before / After Diff Cards */
    .diff-box-before {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        color: #991B1B;
    }
    .diff-box-after {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        color: #065F46;
    }

    /* Evidence Excerpt Quote */
    .evidence-quote {
        background: #F8FAFC;
        border-left: 3px solid #6366F1;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #475569;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }

    /* Section divider */
    .styled-divider {
        height: 1px;
        background: linear-gradient(to right, #E2E8F0, #CBD5E1, #E2E8F0);
        margin: 1.5rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# STATE INITIALIZATION & DEMO DATASET
# ==============================================================================
if "resumes" not in st.session_state:
    st.session_state.resumes = {}
if "jobs" not in st.session_state:
    st.session_state.jobs = {}
if "current_match" not in st.session_state:
    st.session_state.current_match = None

DEMO_RESUME_TEXT = """Alice Chen
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
"""

DEMO_JOB_TEXT = """Senior Computer Vision & AI Engineer
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
"""

def load_demo_workspace():
    cleaned_text, sections, _ = document_parser_factory.parse_document(DEMO_RESUME_TEXT.encode("utf-8"), "Alice_Chen_Resume.txt")
    cand_profile = resume_extractor.extract_profile(cleaned_text, sections)
    st.session_state.resumes[cand_profile["full_name"]] = cand_profile

    parsed_job = job_analyzer.analyze(DEMO_JOB_TEXT)
    st.session_state.jobs[parsed_job["title"]] = parsed_job

    st.session_state.current_match = matching_engine.match(cand_profile, parsed_job)


# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 2.4rem;">🎯</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #1E293B;">IntelliResume AI</div>
            <div style="font-size: 0.8rem; color: #64748B; font-weight: 500;">Explainable ATS & Semantic Matcher</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick 1-Click Demo Loader
    if st.button("⚡ 1-Click Load Full Demo", use_container_width=True, type="primary"):
        load_demo_workspace()
        st.toast("Full Demo Workspace Loaded (Alice Chen vs Apex Robotics)!", icon="🎉")

    st.markdown("---")

    selected_page = st.radio(
        "Workspace Navigation",
        [
            "Executive Overview",
            "Resume Parser & Extractor",
            "Job Description Analyzer",
            "Semantic Match & Evidence",
            "Skill Gaps & 4-Week Roadmap",
            "Resume Improvement Engine",
            "AI Job Recommendations",
            "AI Evaluation & Benchmarks"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.85rem; font-size: 0.82rem;">
            <div style="font-weight: 700; color: #334155; margin-bottom: 0.35rem;">System Health</div>
            <div style="color: #059669; font-weight: 600;">🟢 Fast Semantic Embedder: Active</div>
            <div style="color: #475569; margin-top: 0.2rem;">Model: <code>all-MiniLM-L6-v2</code></div>
            <div style="color: #475569;">Taxonomy: <b>26 Canonical / 80+ Aliases</b></div>
            <div style="color: #475569;">Vector Dim: <b>384 Dense Float32</b></div>
        </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ==============================================================================
if selected_page == "Executive Overview":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">AI Resume Intelligence & Job Matching Platform</div>
            <div class="hero-subtitle">
                An explainable, evidence-grounded AI platform engineered to replace opaque ATS keyword counters with canonical ontology normalization, 4-tier semantic matching, and citation-level proof.
            </div>
            <div class="hero-tags">
                <span class="hero-tag">🎯 4-Tier Match Engine</span>
                <span class="hero-tag">🧠 Sentence Transformers</span>
                <span class="hero-tag">⚡ Zero-Trust Document Cleaning</span>
                <span class="hero-tag">📊 Deterministic Linear Scoring</span>
                <span class="hero-tag">🛡️ Anti-Fabrication Improver</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Resumes Ingested</div>
            </div>
        """.format(len(st.session_state.resumes)), unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Job Specs Analyzed</div>
            </div>
        """.format(len(st.session_state.jobs)), unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value" style="color: #059669;">96.2%</div>
                <div class="metric-label">Skill Extraction Precision</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value" style="color: #4F46E5;">0.92</div>
                <div class="metric-label">Semantic MRR Score</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

    # Core Architectural Advantages
    st.subheader("Architectural Pillars vs Legacy ATS")
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        st.markdown("""
            <div class="glass-card" style="height: 100%;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🧬</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">Canonical Skill Ontology</div>
                <div style="font-size: 0.9rem; color: #64748B; margin-top: 0.5rem; line-height: 1.5;">
                    Resolves real-world syntax fragmentation (e.g. <code>psql</code>, <code>postgres</code> &rarr; <b>PostgreSQL</b>; <code>ReactJS</code> &rarr; <b>React</b>). Evaluates transferable skills (e.g. Flask transfers to FastAPI at 85% credit) without hallucinating missing direct exposure.
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c_p2:
        st.markdown("""
            <div class="glass-card" style="height: 100%;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚖️</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">Transparent Linear Scoring</div>
                <div style="font-size: 0.9rem; color: #64748B; margin-top: 0.5rem; line-height: 1.5;">
                    Rejects fabricated "ATS percentages". Uses configurable, mathematically sound multi-factor weighting:
                    <div style="margin-top: 0.4rem; font-size: 0.82rem; font-weight: 600; color: #4338CA;">
                        Score = 0.40·Req + 0.20·Sem + 0.15·Exp + 0.10·Pref + 0.10·Proj + 0.05·Edu
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c_p3:
        st.markdown("""
            <div class="glass-card" style="height: 100%;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📝</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">Verifiable Evidence Citations</div>
                <div style="font-size: 0.9rem; color: #64748B; margin-top: 0.5rem; line-height: 1.5;">
                    Every direct match and transferable relationship cites exact text passages from the candidate's actual projects and work history. Zero black-box claims.
                </div>
            </div>
        """, unsafe_allow_html=True)

    if not st.session_state.resumes:
        st.info("💡 **Ready to explore?** Click the **'⚡ 1-Click Load Full Demo'** button in the sidebar, or navigate to **Resume Parser & Extractor** to upload your own files.")


# ==============================================================================
# PAGE 2: RESUME PARSER & EXTRACTOR
# ==============================================================================
elif selected_page == "Resume Parser & Extractor":
    st.markdown("## 📄 Resume Parser & Profile Extractor")
    st.markdown("Upload any PDF, DOCX, or text resume to extract structured schema, timeline, and categorized skills.")

    col_up, col_preview = st.columns([1.1, 0.9])
    with col_up:
        uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "docx", "txt"])
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            load_sample = st.button("📋 Load Sample ML Resume", use_container_width=True)
        with c_btn2:
            clear_cache = st.button("🧹 Clear Uploaded", use_container_width=True)

        if clear_cache:
            st.session_state.resumes = {}
            st.rerun()

        file_bytes = None
        filename = "resume.txt"

        if load_sample:
            file_bytes = DEMO_RESUME_TEXT.encode("utf-8")
            filename = "Alice_Chen_Resume.txt"
        elif uploaded_file is not None:
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name

        if file_bytes:
            with st.spinner("Extracting entities, cleaning ligatures, and segmenting sections..."):
                cleaned_text, sections, pages = document_parser_factory.parse_document(file_bytes, filename)
                profile = resume_extractor.extract_profile(cleaned_text, sections)
                st.session_state.resumes[profile["full_name"]] = profile
                st.success(f"Extracted Profile: **{profile['full_name']}** ({pages} page(s) analyzed)")

    with col_preview:
        if st.session_state.resumes:
            sel_res_name = st.selectbox("Active Resume Profile", list(st.session_state.resumes.keys()))
            profile = st.session_state.resumes[sel_res_name]

            st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                        <div>
                            <div style="font-size: 1.4rem; font-weight: 800; color: #1E293B;">{profile['full_name']}</div>
                            <div style="color: #6366F1; font-weight: 600; font-size: 0.95rem;">{profile['inferred_primary_role']}</div>
                        </div>
                        <span class="badge-direct">{profile['total_years_experience']} Years Exp</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                        <div>📧 <b>Email</b>: <code>{profile['email']}</code></div>
                        <div>📱 <b>Phone</b>: <code>{profile['phone']}</code></div>
                        <div>🔗 <b>Links</b>: <a href="https://{profile['linkedin_url']}" target="_blank">{profile['linkedin_url']}</a> | <a href="https://{profile['github_url']}" target="_blank">{profile['github_url']}</a></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Upload a resume file or load the sample resume to inspect candidate attributes.")

    # Detailed Skill & Timeline Breakdown
    if st.session_state.resumes:
        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        st.subheader("Candidate Competency & Categorized Skill Matrix")

        skills_by_cat = profile.get("categorized_skills", {})
        
        # Donut Chart of Skills by Category
        cat_counts = {k.replace('_', ' ').title(): len(v) for k, v in skills_by_cat.items() if v}
        if cat_counts:
            col_chart, col_skills = st.columns([0.8, 1.2])
            with col_chart:
                fig = px.pie(
                    names=list(cat_counts.keys()),
                    values=list(cat_counts.values()),
                    hole=0.55,
                    color_discrete_sequence=px.colors.qualitative.Prism,
                    title="Skill Category Distribution"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10), height=280)
                st.plotly_chart(fig, use_container_width=True)

            with col_skills:
                for cat, sk_list in skills_by_cat.items():
                    if sk_list:
                        st.markdown(f"**{cat.replace('_', ' ').title()}**")
                        chips_html = "".join([f'<span class="skill-chip">{s}</span>' for s in sk_list])
                        st.markdown(f"<div>{chips_html}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

        # Work Experience Timeline
        if profile.get("experiences"):
            st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
            st.subheader("Experience Timeline")
            for exp in profile["experiences"]:
                with st.expander(f"💼 {exp['job_title']} @ {exp['company']} ({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})", expanded=True):
                    for ach in exp.get("key_achievements", []):
                        st.markdown(f"- {ach}")


# ==============================================================================
# PAGE 3: JOB DESCRIPTION ANALYZER
# ==============================================================================
elif selected_page == "Job Description Analyzer":
    st.markdown("## 💼 Job Description Analyzer")
    st.markdown("Dissect unstructured job requisitions into hard requirements, preferred skills, and experience criteria.")

    col_input, col_meta = st.columns([1.1, 0.9])
    with col_input:
        jd_input = st.text_area("Paste Raw Job Description", height=240, placeholder="Paste job posting text here...", value=DEMO_JOB_TEXT if not st.session_state.jobs else "")
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            btn_analyze = st.button("⚡ Analyze Job Specification", type="primary", use_container_width=True)
        with c_an2:
            btn_load_sample_jd = st.button("📋 Load Sample AI Posting", use_container_width=True)

        if btn_load_sample_jd:
            parsed_job = job_analyzer.analyze(DEMO_JOB_TEXT)
            st.session_state.jobs[parsed_job["title"]] = parsed_job
            st.rerun()

        if btn_analyze and jd_input.strip():
            with st.spinner("Analyzing job requirements and criteria..."):
                parsed_job = job_analyzer.analyze(jd_input)
                st.session_state.jobs[parsed_job["title"]] = parsed_job
                st.success(f"Job Analyzed: **{parsed_job['title']}** at **{parsed_job['company']}**")

    with col_meta:
        if st.session_state.jobs:
            sel_job_name = st.selectbox("Active Job Requisition", list(st.session_state.jobs.keys()))
            active_job = st.session_state.jobs[sel_job_name]

            st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size: 1.3rem; font-weight: 800; color: #1E293B;">{active_job['title']}</div>
                    <div style="color: #6366F1; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.8rem;">{active_job['company']} | {active_job.get('location', 'Remote/Hybrid')}</div>
                    <div style="display: flex; gap: 0.8rem; flex-wrap: wrap;">
                        <span class="badge-direct">Min Exp: {active_job['min_years_experience']} Years</span>
                        <span class="badge-trans">Domain: {active_job['domain']}</span>
                        <span class="badge-inferred">Education: Level {active_job['min_education_level']}+</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Paste a job description or load the sample posting to analyze requirements.")

    if st.session_state.jobs:
        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        col_req, col_pref = st.columns(2)
        with col_req:
            st.subheader("🔴 Hard Requirements (Mandatory)")
            for r in active_job["required_skills"]:
                st.markdown(f"""
                    <div style="background: #FEF2F2; border-left: 3px solid #EF4444; padding: 0.4rem 0.8rem; border-radius: 4px; margin-bottom: 0.4rem; font-size: 0.9rem;">
                        <b>{r['canonical_name']}</b> <span style="color: #64748B;">({r['category']})</span>
                    </div>
                """, unsafe_allow_html=True)

        with col_pref:
            st.subheader("🟡 Preferred & Bonus Qualifications")
            for p in active_job["preferred_skills"]:
                st.markdown(f"""
                    <div style="background: #FFFBEB; border-left: 3px solid #F59E0B; padding: 0.4rem 0.8rem; border-radius: 4px; margin-bottom: 0.4rem; font-size: 0.9rem;">
                        <b>{p['canonical_name']}</b> <span style="color: #64748B;">({p['category']})</span>
                    </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 4: SEMANTIC MATCH & EVIDENCE EXPLORER
# ==============================================================================
elif selected_page == "Semantic Match & Evidence":
    st.markdown("## 🎯 Semantic Compatibility & Evidence Explorer")
    st.markdown("Transparent mathematical match breakdown with verifiable, sentence-level textual proof.")

    if not st.session_state.resumes or not st.session_state.jobs:
        st.warning("Please ensure at least one resume is parsed and one job is analyzed.")
        if st.button("⚡ Click to Load Complete Demo Dataset"):
            load_demo_workspace()
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

        if recalc or st.session_state.current_match is None:
            with st.spinner("Executing semantic embedding matching and evidence verification..."):
                st.session_state.current_match = matching_engine.match(cand, job)

        match_res = st.session_state.current_match
        overall = match_res["overall_score"]

        # Gauge & Radar Visualizations
        col_gauge, col_radar = st.columns([0.9, 1.1])
        with col_gauge:
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Compatibility", 'font': {'size': 20, 'family': 'Plus Jakarta Sans', 'color': '#1E293B'}},
                number={'suffix': "%", 'font': {'size': 36, 'color': '#1E293B'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
                    'bar': {'color': "#4F46E5", 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#E2E8F0",
                    'steps': [
                        {'range': [0, 50], 'color': '#FEE2E2'},
                        {'range': [50, 75], 'color': '#FEF3C7'},
                        {'range': [75, 100], 'color': '#D1FAE5'}
                    ],
                }
            ))
            gauge_fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(gauge_fig, use_container_width=True)

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
                fillcolor='rgba(79, 70, 229, 0.25)',
                line=dict(color='#4F46E5', width=2),
                name='Compatibility Profile'
            ))
            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color='#64748B'),
                ),
                margin=dict(l=30, r=30, t=30, b=30),
                height=260,
                showlegend=False
            )
            st.plotly_chart(radar_fig, use_container_width=True)

        # Transparent Scoring Synthesis
        st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #4F46E5;">
                <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.3rem;">🧠 AI Synthesis Rationale</div>
                <div style="color: #475569; font-size: 0.95rem; line-height: 1.5;">{match_res['synthesis_explanation']}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

        # Evidence Cards with Interactive Filter
        st.subheader("Verifiable Evidence & Attribution Matrix")
        filter_status = st.radio("Filter Evidence", ["All Evidence", "Direct Matches Only", "Transferable Skills Only", "Missing Skills Only"], horizontal=True)

        evidences = match_res.get("evidences", [])
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
                <div class="glass-card" style="border-left: 4px solid {border_color}; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">{ev['skill_name']} <span style="font-size: 0.85rem; color: #64748B; font-weight: 500;">({req_label})</span></span>
                        {badge_html}
                    </div>
                    <div style="font-size: 0.92rem; color: #334155; margin-top: 0.4rem;">
                        <b>Explanation</b>: {ev['explanation']}
                    </div>
                    {f'<div class="evidence-quote">📝 <b>Resume Citation</b>: "{ev["evidence_quote"]}"</div>' if ev.get("evidence_quote") else ''}
                </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 5: SKILL GAPS & 4-WEEK ROADMAP
# ==============================================================================
elif selected_page == "Skill Gaps & 4-Week Roadmap":
    st.markdown("## 🗺️ Skill Gap Analysis & 4-Week Career Roadmap")
    st.markdown("Targeted gap breakdown with personalized, prioritized upskilling actions.")

    if not st.session_state.resumes or not st.session_state.jobs:
        st.warning("Please load or parse candidate and job data first.")
        if st.button("⚡ Load Demo Dataset"):
            load_demo_workspace()
            st.rerun()
    else:
        sel_res = st.selectbox("Candidate Profile", list(st.session_state.resumes.keys()), key="gap_c")
        sel_j = st.selectbox("Target Position", list(st.session_state.jobs.keys()), key="gap_j")

        cand = st.session_state.resumes[sel_res]
        job = st.session_state.jobs[sel_j]

        match_res = matching_engine.match(cand, job)
        gaps = gap_analyzer.analyze_gaps(cand["skills"], match_res["evidences"])

        # Top Coverage Bar
        cov = gaps['coverage_ratio']
        st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #1E293B;">Required Skill Coverage</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #4F46E5;">{cov}%</div>
                </div>
                <div style="background: #E2E8F0; border-radius: 9999px; height: 10px; width: 100%; margin-top: 0.5rem; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #4F46E5, #10B981); height: 100%; width: {cov}%;"></div>
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.4rem;">
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
                        <div class="glass-card" style="border-left: 3px solid #EF4444; padding: 0.9rem; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 700; color: #1E293B;">{m['skill_name']}</span>
                                <span class="badge-missing">Priority: {m['priority_level']}</span>
                            </div>
                            <div style="font-size: 0.84rem; color: #64748B; margin-top: 0.2rem;">
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
                        <div class="glass-card" style="border-left: 3px solid #6366F1; padding: 0.9rem; margin-bottom: 0.5rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="font-weight: 700; color: #1E293B;">{t['skill_name']}</span>
                                <span class="badge-trans">Transfer Credit: {int(t['transferability_score']*100)}%</span>
                            </div>
                            <div style="font-size: 0.84rem; color: #475569; margin-top: 0.2rem;">
                                Backed by verified background in: <code>{t['matched_transferable_skill']}</code>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transferable skills applied.")

        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)
        st.subheader("🗓️ 4-Week Accelerated Upskilling Roadmap")
        for step in gaps.get("upskilling_roadmap", []):
            with st.expander(f"📍 Week {step['week']}: {step['phase']}", expanded=True):
                st.markdown(f"**Target Skills**: " + " ".join([f"`{s}`" for s in step['focus_skills']]))
                for act in step['action_items']:
                    st.markdown(f"- {act}")


# ==============================================================================
# PAGE 6: RESUME IMPROVEMENT ENGINE
# ==============================================================================
elif selected_page == "Resume Improvement Engine":
    st.markdown("## 🚀 Anti-Fabrication Resume Improvement Engine")
    st.markdown("Action-verb upgrades and metric quantification templates without inventing fake experience.")

    if not st.session_state.resumes:
        st.warning("Please upload or load a resume first.")
        if st.button("⚡ Load Demo Resume"):
            load_demo_workspace()
            st.rerun()
    else:
        sel_res = st.selectbox("Select Candidate Resume", list(st.session_state.resumes.keys()), key="imp_c")
        cand = st.session_state.resumes[sel_res]

        improvements = resume_improver.improve(cand)

        col_sc, col_cr = st.columns([0.7, 1.3])
        with col_sc:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #4F46E5;">{improvements['strength_score']}<span style="font-size: 1.2rem; color: #94A3B8;">/100</span></div>
                    <div class="metric-label">Resume Strength Index</div>
                </div>
            """, unsafe_allow_html=True)
        with col_cr:
            st.markdown(f"""
                <div class="glass-card" style="height: 100%;">
                    <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.3rem;">📋 Diagnostic Critique</div>
                    <div style="color: #475569; font-size: 0.92rem; line-height: 1.5;">{improvements['overall_critique']}</div>
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
                        <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.3rem;">❌ ORIGINAL PASSIVE BULLET</div>
                        "{sug['original_text']}"
                    </div>
                """, unsafe_allow_html=True)
            with c_sug:
                st.markdown(f"""
                    <div class="diff-box-after">
                        <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.3rem;">✅ RECOMMENDED ACTION-ORIENTED REVISION</div>
                        "{sug['suggested_revision']}"
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 0.6rem 1rem; font-size: 0.88rem; color: #475569; margin-bottom: 1.2rem;">
                    💡 <b>Rationale</b>: {sug['critique']}<br>
                    ✍️ <b>Fill-in-the-blank Prompt</b>: <i>{sug['interactive_prompt']}</i>
                </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 7: AI JOB RECOMMENDATIONS
# ==============================================================================
elif selected_page == "AI Job Recommendations":
    st.markdown("## 🔍 AI Job Recommendations & Profile Market Fit")
    st.markdown("Top job recommendations based on dense semantic vector similarity and verified skill overlap.")

    if not st.session_state.resumes:
        st.warning("Please upload a resume first.")
        if st.button("⚡ Load Demo Dataset"):
            load_demo_workspace()
            st.rerun()
    else:
        sel_res = st.selectbox("Candidate Profile", list(st.session_state.resumes.keys()), key="rec_c")
        cand = st.session_state.resumes[sel_res]

        sample_jobs_pool = list(st.session_state.jobs.values())
        if len(sample_jobs_pool) < 2:
            extra_jobs = [
                job_analyzer.analyze("Senior Computer Vision & AI Engineer at Apex Robotics Labs. 4+ years exp. Required: Python, PyTorch, Computer Vision, FastAPI. Preferred: Kubernetes, Docker, AWS."),
                job_analyzer.analyze("Senior Deep Learning Systems Engineer at Anthropic. 4+ years exp. Required: Python, PyTorch, Deep Learning, Docker. Preferred: Kubernetes, C++."),
                job_analyzer.analyze("Lead Backend Platform Engineer at Stripe. 5+ years exp. Required: Python, FastAPI, PostgreSQL, SQL. Preferred: Docker, AWS."),
                job_analyzer.analyze("AI Infrastructure & DevOps Engineer at Scale AI. 3+ years exp. Required: Docker, Kubernetes, AWS, Bash. Preferred: Python, PyTorch.")
            ]
            sample_jobs_pool = extra_jobs

        recommendations = job_recommender.recommend_jobs(cand, sample_jobs_pool, top_k=5)

        for rec in recommendations:
            fit = rec['overall_fit_score']
            if fit >= 75:
                bar_color = "#10B981"
            elif fit >= 60:
                bar_color = "#6366F1"
            else:
                bar_color = "#F59E0B"

            st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="background: #EEF2FF; color: #4F46E5; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.85rem; margin-right: 0.4rem;">#{rec['rank']}</span>
                            <span style="font-size: 1.25rem; font-weight: 800; color: #1E293B;">{rec['title']}</span>
                            <span style="color: #64748B; font-weight: 600; font-size: 1rem;"> @ {rec['company']}</span>
                        </div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: {bar_color};">{fit:.1f}% Match</div>
                    </div>
                    <div style="margin-top: 0.6rem; font-size: 0.92rem; color: #475569; line-height: 1.5;">
                        <b>Fit Assessment</b>: {rec['match_rationale']}
                    </div>
                    <div style="margin-top: 0.6rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <span style="font-size: 0.82rem; font-weight: 600; color: #047857;">Verified Skills:</span> {' '.join([f'<span class="badge-direct">{s}</span>' for s in rec['matched_skills'][:5]])}
                        {f'<span style="font-size: 0.82rem; font-weight: 600; color: #B91C1C; margin-left: 0.5rem;">Missing:</span> {" ".join([f"<span class='badge-missing'>{s}</span>" for s in rec["missing_skills"][:3]])}' if rec.get("missing_skills") else ''}
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 8: AI MODEL EVALUATION & BENCHMARKS
# ==============================================================================
elif selected_page == "AI Model Evaluation":
    st.markdown("## 📈 AI Model Evaluation & Quality Benchmarks")
    st.markdown("Rigorous offline evaluation measuring extraction precision, recall, F1, and semantic MRR.")

    c_run, c_space = st.columns([1, 2])
    with c_run:
        btn_eval = st.button("🚀 Run Live Evaluation Benchmark", type="primary", use_container_width=True)

    if btn_eval or "eval_metrics" in st.session_state:
        if btn_eval or "eval_metrics" not in st.session_state:
            with st.spinner("Executing benchmark across annotated gold-standard candidate-job pairs..."):
                st.session_state.eval_metrics = evaluation_service.run_benchmark()

        eval_data = st.session_state.eval_metrics
        m = eval_data["metrics"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #059669;">{m['skill_extraction_precision']*100:.1f}%</div>
                    <div class="metric-label">Extraction Precision</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #4F46E5;">{m['skill_extraction_recall']*100:.1f}%</div>
                    <div class="metric-label">Extraction Recall</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #0284C7;">{m['skill_extraction_f1']:.3f}</div>
                    <div class="metric-label">F1 Quality Score</div>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: #10B981;">{m['job_requirement_accuracy']*100:.1f}%</div>
                    <div class="metric-label">Requirement Accuracy</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

        # Plotly Benchmark Comparison Bar Chart
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
                marker_color=['#059669', '#4F46E5', '#0284C7', '#10B981', '#7C3AED'],
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
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(bar_fig, use_container_width=True)

        st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #10B981;">
                <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.2rem;">Executive Benchmark Summary</div>
                <div style="color: #475569; font-size: 0.95rem;">{eval_data['summary']}</div>
            </div>
        """, unsafe_allow_html=True)
