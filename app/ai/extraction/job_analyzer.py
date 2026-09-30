import re
from typing import Dict, List, Any, Tuple
from app.ai.extraction.skill_extractor import skill_extractor
from app.core.constants import DegreeLevel


class JobDescriptionAnalyzer:
    EXP_YEARS_PATTERN = re.compile(
        r"(\d{1,2})\+?\s*(?:to|-)?\s*(\d{1,2})?\s*(?:years?|yrs?)(?:\s*of\s*experience)?",
        re.IGNORECASE
    )

    REQUIRED_HEADERS = [
        "requirements", "qualifications", "minimum qualifications", "what you need",
        "must have", "required skills", "basic qualifications", "who you are"
    ]

    PREFERRED_HEADERS = [
        "preferred qualifications", "nice to have", "bonus", "bonus points",
        "preferred skills", "what gives you an edge", "desired skills", "plus"
    ]

    RESPONSIBILITY_HEADERS = [
        "responsibilities", "what you will do", "role responsibilities",
        "duties", "key responsibilities", "day to day"
    ]

    @classmethod
    def analyze(cls, text: str, title: str = "", company: str = "") -> Dict[str, Any]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        detected_title = title
        detected_company = company

        if not detected_title and lines:
            first_line = lines[0]
            if len(first_line) < 80:
                detected_title = first_line

        if not detected_company:
            for line in lines[:5]:
                if any(w in line.lower() for w in ["at ", "with ", "company:", "inc", "corp", "technologies", "labs"]):
                    comp = re.sub(r"(?i)^(about|at|join)\s+", "", line).split("-")[0].strip()
                    if comp and len(comp) < 50:
                        detected_company = comp
                        break

        req_lines, pref_lines, resp_lines, other_lines = cls._split_jd_sections(lines)
        min_years = cls._extract_min_experience(text)
        min_edu = cls._extract_min_education(text)

        req_skills_raw = skill_extractor.extract_skills("\n".join(req_lines) or text)
        req_skills_canonical = [s["canonical_name"] for s in req_skills_raw]

        pref_skills_raw = skill_extractor.extract_skills("\n".join(pref_lines))
        pref_skills_filtered = [
            s for s in pref_skills_raw if s["canonical_name"] not in req_skills_canonical
        ]

        if not pref_skills_filtered and len(req_skills_raw) > 4:
            split_idx = int(len(req_skills_raw) * 0.7)
            primary_req = req_skills_raw[:split_idx]
            pref_skills_filtered = req_skills_raw[split_idx:]
            req_skills_raw = primary_req

        responsibilities = [
            re.sub(r"^[*•\->\s]+", "", r).strip()
            for r in resp_lines if len(r) > 20
        ][:8]

        return {
            "title": detected_title or "Software Engineer",
            "company": detected_company or "Hiring Organization",
            "location": "Remote / Hybrid",
            "min_years_experience": min_years,
            "min_education_level": min_edu,
            "domain": cls._detect_domain(text),
            "responsibilities": responsibilities,
            "required_skills": req_skills_raw,
            "preferred_skills": pref_skills_filtered,
            "raw_text": text
        }

    @classmethod
    def _split_jd_sections(cls, lines: List[str]) -> Tuple[List[str], List[str], List[str], List[str]]:
        req_lines = []
        pref_lines = []
        resp_lines = []
        other_lines = []

        current_bucket = "other"

        for line in lines:
            line_lower = line.lower().strip().replace(":", "").replace("-", "")

            if any(h in line_lower for h in cls.PREFERRED_HEADERS):
                current_bucket = "pref"
                continue
            elif any(h in line_lower for h in cls.REQUIRED_HEADERS):
                current_bucket = "req"
                continue
            elif any(h in line_lower for h in cls.RESPONSIBILITY_HEADERS):
                current_bucket = "resp"
                continue

            if current_bucket == "req":
                req_lines.append(line)
            elif current_bucket == "pref":
                pref_lines.append(line)
            elif current_bucket == "resp":
                resp_lines.append(line)
            else:
                other_lines.append(line)

        return req_lines, pref_lines, resp_lines, other_lines

    @classmethod
    def _extract_min_experience(cls, text: str) -> float:
        matches = cls.EXP_YEARS_PATTERN.findall(text)
        if matches:
            first_num = float(matches[0][0])
            return first_num
        return 2.0

    @classmethod
    def _extract_min_education(cls, text: str) -> int:
        text_lower = text.lower()
        if "phd" in text_lower or "doctorate" in text_lower:
            return int(DegreeLevel.DOCTORATE)
        elif "master" in text_lower or "ms" in text_lower or "m.s." in text_lower:
            return int(DegreeLevel.MASTERS)
        elif "bachelor" in text_lower or "bs" in text_lower or "b.s." in text_lower or "degree" in text_lower:
            return int(DegreeLevel.BACHELORS)
        return int(DegreeLevel.BACHELORS)

    @classmethod
    def _detect_domain(cls, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["machine learning", "deep learning", "ai", "llm", "nlp"]):
            return "Artificial Intelligence / Machine Learning"
        elif any(w in text_lower for w in ["fintech", "banking", "payment", "trading"]):
            return "Financial Technology (FinTech)"
        elif any(w in text_lower for w in ["cloud", "devops", "infrastructure", "kubernetes", "sre"]):
            return "Cloud Infrastructure & DevOps"
        elif any(w in text_lower for w in ["health", "biotech", "medical", "clinical"]):
            return "Healthcare & Life Sciences"
        return "Software & Internet Technologies"


job_analyzer = JobDescriptionAnalyzer()
