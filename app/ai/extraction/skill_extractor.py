import re
from typing import List, Dict, Any, Set
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.core.constants import SkillCategory


class SkillExtractor:
    # Short tokens that require exact case matching or word boundaries to prevent false positives
    CASE_SENSITIVE_ALIASES = {"r", "c", "go", "tf", "py"}

    def __init__(self):
        self.normalizer = skill_normalizer
        self._compile_patterns()

    def _compile_patterns(self):
        self.alias_patterns = {}
        # Sort by length descending to match longer, specific phrases first
        sorted_aliases = sorted(
            self.normalizer.alias_to_canonical.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for alias, canonical in sorted_aliases:
            alias_lower = alias.lower()
            if alias_lower in self.CASE_SENSITIVE_ALIASES:
                # Require uppercase or exact boundary token to avoid matching English words
                pattern = re.compile(rf"\b{re.escape(alias.upper())}\b")
            elif len(alias) <= 2:
                pattern = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(alias)}(?![a-zA-Z0-9_])", re.IGNORECASE)
            elif alias in ("c++", "c#", ".net"):
                pattern = re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(alias)}(?![a-zA-Z0-9_#+])", re.IGNORECASE)
            else:
                pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)

            self.alias_patterns[alias] = (pattern, canonical)

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        if not text:
            return []
        # Abbreviation- and tech-aware sentence segmentation:
        # Splits on newlines, semicolons, or sentence-ending periods followed by whitespace and a capital letter
        # Preserves version numbers (3.11), library suffixes (Node.js, Vue.js), decimals (99.9%), and abbreviations
        raw_chunks = re.split(r"(?:\r?\n)+|;\s*|(?<=[a-zA-Z0-9\)])\.\s+(?=[A-Z0-9])", text)
        sentences = [c.strip() for c in raw_chunks if c and len(c.strip()) > 1]
        return sentences

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []

        sentences = self.split_sentences(text)
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
