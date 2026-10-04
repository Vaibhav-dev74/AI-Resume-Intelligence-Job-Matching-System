"""
Synthetic demo candidate resumes and target job requisition presets for demonstration and testing.
All candidates and job listings are synthetic demonstration profiles.
"""
from typing import Dict, Any

PRESET_RESUMES: Dict[str, str] = {
    "[Demo Candidate] Alice Chen (Senior ML Engineer) — Synthetic Demo Profile": """Alice Chen
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

    "[Demo Candidate] David Miller (Backend Platform Engineer) — Synthetic Demo Profile": """David Miller
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

    "[Demo Candidate] Elena Rostova (Junior NLP / Python Developer) — Synthetic Demo Profile": """Elena Rostova
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

PRESET_JOBS: Dict[str, str] = {
    "[Demo Job] Apex Robotics (Senior AI/CV Engineer) — Synthetic Job Description": """Senior Computer Vision & AI Engineer
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

    "[Demo Job] Stripe (Senior Backend Platform Engineer) — Synthetic Job Description": """Senior Backend Platform Engineer
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

    "[Demo Job] DeepMind (Research Systems Engineer - NLP) — Synthetic Job Description": """Research Systems Engineer - NLP & Foundation Models
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

