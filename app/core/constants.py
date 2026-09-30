from enum import Enum
from typing import Dict


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD_DEVOPS = "cloud_devops"
    AI_ML = "ai_ml"
    DATA_ENGINEERING = "data_engineering"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


class MatchStatus(str, Enum):
    DIRECT_MATCH = "direct_match"
    TRANSFERABLE_MATCH = "transferable_match"
    INFERRED = "inferred"
    MISSING = "missing"


class DegreeLevel(int, Enum):
    HIGH_SCHOOL = 1
    ASSOCIATE = 2
    BACHELORS = 3
    MASTERS = 4
    DOCTORATE = 5


DEGREE_MAPPING: Dict[str, DegreeLevel] = {
    "phd": DegreeLevel.DOCTORATE,
    "ph.d": DegreeLevel.DOCTORATE,
    "doctorate": DegreeLevel.DOCTORATE,
    "doctor of philosophy": DegreeLevel.DOCTORATE,
    "master": DegreeLevel.MASTERS,
    "masters": DegreeLevel.MASTERS,
    "m.s": DegreeLevel.MASTERS,
    "ms": DegreeLevel.MASTERS,
    "m.sc": DegreeLevel.MASTERS,
    "msc": DegreeLevel.MASTERS,
    "m.tech": DegreeLevel.MASTERS,
    "mtech": DegreeLevel.MASTERS,
    "mba": DegreeLevel.MASTERS,
    "bachelor": DegreeLevel.BACHELORS,
    "bachelors": DegreeLevel.BACHELORS,
    "b.s": DegreeLevel.BACHELORS,
    "bs": DegreeLevel.BACHELORS,
    "b.sc": DegreeLevel.BACHELORS,
    "bsc": DegreeLevel.BACHELORS,
    "b.tech": DegreeLevel.BACHELORS,
    "btech": DegreeLevel.BACHELORS,
    "b.e": DegreeLevel.BACHELORS,
    "be": DegreeLevel.BACHELORS,
    "associate": DegreeLevel.ASSOCIATE,
    "high school": DegreeLevel.HIGH_SCHOOL,
    "diploma": DegreeLevel.HIGH_SCHOOL,
}

SECTION_TITLES = {
    "summary": ["summary", "professional summary", "profile", "about me", "objective", "career objective"],
    "experience": ["experience", "work experience", "employment history", "work history", "professional experience", "internships", "internship experience"],
    "education": ["education", "academic background", "academic qualifications", "qualifications", "academics"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "proficiencies", "skills & tools", "technical proficiencies"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects"],
    "certifications": ["certifications", "licenses & certifications", "certificates", "credentials", "professional certifications"],
    "achievements": ["achievements", "honors & awards", "awards", "accomplishments", "publications"]
}
