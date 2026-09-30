import re
from typing import List, Dict, Any
from app.core.constants import DEGREE_MAPPING, DegreeLevel


class EducationExtractor:
    YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
    GPA_PATTERN = re.compile(r"\b(?:GPA|gpa)[:\s]*([0-4]\.\d{1,2}(?:/[0-4]\.\d{1,2})?)\b")

    DEGREE_PATTERNS = [
        (re.compile(r"\b(ph\.?d|doctorate|doctor of philosophy)\b", re.IGNORECASE), DegreeLevel.DOCTORATE, "Ph.D."),
        (re.compile(r"\b(m\.?s\.?c?|m\.?tech|masters?|mba|master of (?:science|engineering|arts|business))\b", re.IGNORECASE), DegreeLevel.MASTERS, "Master's Degree"),
        (re.compile(r"\b(b\.?s\.?c?|b\.?tech|b\.?e\.?|bachelors?|bachelor of (?:science|engineering|arts|technology))\b", re.IGNORECASE), DegreeLevel.BACHELORS, "Bachelor's Degree"),
        (re.compile(r"\b(associate(?:'s)? degree|associate of (?:science|arts))\b", re.IGNORECASE), DegreeLevel.ASSOCIATE, "Associate Degree"),
    ]

    INSTITUTION_KEYWORDS = [
        "university", "college", "institute", "polytechnic", "school", "academy"
    ]

    @classmethod
    def extract(cls, education_text: str, fallback_text: str = "") -> List[Dict[str, Any]]:
        text = education_text if education_text.strip() else fallback_text
        if not text:
            return []

        entries = []
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        if len(blocks) <= 1:
            blocks = [line.strip() for line in text.split("\n") if line.strip()]

        for block in blocks:
            detected_degree = None
            detected_level = DegreeLevel.BACHELORS
            canonical_degree = "Bachelor's Degree"

            for pattern, level, label in cls.DEGREE_PATTERNS:
                m = pattern.search(block)
                if m:
                    detected_degree = m.group(0)
                    detected_level = level
                    canonical_degree = label
                    break

            institution = cls._extract_institution(block)
            years = cls.YEAR_PATTERN.findall(block)
            grad_year = int(years[-1]) if years else None

            gpa_match = cls.GPA_PATTERN.search(block)
            gpa = gpa_match.group(1) if gpa_match else None

            if institution or detected_degree:
                entries.append({
                    "institution": institution or "Accredited University / Institution",
                    "degree": canonical_degree if detected_degree else "Degree Program",
                    "degree_level": int(detected_level),
                    "field_of_study": cls._extract_field_of_study(block),
                    "graduation_year": grad_year,
                    "gpa": gpa
                })

        return entries

    @classmethod
    def _extract_institution(cls, text: str) -> str:
        for line in text.split("\n"):
            clean_line = line.strip()
            for kw in cls.INSTITUTION_KEYWORDS:
                if kw in clean_line.lower():
                    cleaned = re.sub(r"[,|\-].*", "", clean_line).strip()
                    return cleaned
        return ""

    @classmethod
    def _extract_field_of_study(cls, text: str) -> str:
        fields = [
            "Computer Science", "Software Engineering", "Data Science", "Artificial Intelligence",
            "Machine Learning", "Information Technology", "Electrical Engineering", "Mathematics",
            "Statistics", "Physics", "Mechanical Engineering", "Business Administration"
        ]
        text_lower = text.lower()
        for f in fields:
            if f.lower() in text_lower:
                return f
        return "Computer Science or Related Field"


education_extractor = EducationExtractor()
