import re
from typing import List, Dict, Any, Set
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.core.constants import SkillCategory


class SkillExtractor:
    def __init__(self):
        self.normalizer = skill_normalizer
        self._compile_patterns()

    def _compile_patterns(self):
        self.alias_patterns = {}
        for alias, canonical in self.normalizer.alias_to_canonical.items():
            if len(alias) <= 2:
                pattern = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(alias)}(?![a-zA-Z0-9_])", re.IGNORECASE)
            elif alias in ("c++", "c#", ".net"):
                pattern = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(alias)}", re.IGNORECASE)
            else:
                pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)

            self.alias_patterns[alias] = (pattern, canonical)

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []

        sentences = [s.strip() for s in re.split(r"[.\n\r]+", text) if s.strip()]
        found_skills: Dict[str, Dict[str, Any]] = {}

        for sentence in sentences:
            for alias, (pattern, canonical) in self.alias_patterns.items():
                match = pattern.search(sentence)
                if match:
                    node = self.normalizer.canonical_nodes.get(canonical)
                    category = node.category.value if node else SkillCategory.TOOL.value

                    if canonical not in found_skills:
                        found_skills[canonical] = {
                            "canonical_name": canonical,
                            "category": category,
                            "raw_extracted_text": match.group(0),
                            "evidence_context": sentence[:250],
                            "confidence_score": 1.0
                        }

        return list(found_skills.values())

    def categorize_skills(self, extracted_skills: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        categorized: Dict[str, List[str]] = {}
        for s in extracted_skills:
            cat = s["category"]
            categorized.setdefault(cat, []).append(s["canonical_name"])
        return categorized


skill_extractor = SkillExtractor()
