import re
from typing import Dict, List
from app.core.constants import SECTION_TITLES
from app.document_processing.sanitizer import text_sanitizer


class SectionSegmenter:
    def __init__(self):
        self.header_lookup: Dict[str, str] = {}
        for canonical, phrases in SECTION_TITLES.items():
            for p in phrases:
                self.header_lookup[p.lower().strip()] = canonical

    def _is_header(self, line: str) -> str:
        clean = line.strip().lower()
        clean_stripped = re.sub(r"[:\-_|]", "", clean).strip()

        if clean_stripped in self.header_lookup:
            return self.header_lookup[clean_stripped]

        words = clean_stripped.split()
        if len(words) <= 4:
            for phrase, canonical in self.header_lookup.items():
                if clean_stripped == phrase or clean_stripped.startswith(phrase + " "):
                    return canonical

        return ""

    def segment(self, raw_text: str) -> Dict[str, str]:
        cleaned = text_sanitizer.clean(raw_text)
        lines = cleaned.split("\n")

        sections: Dict[str, List[str]] = {
            "header": [],
            "summary": [],
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "other": []
        }

        current_section = "header"

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            detected = self._is_header(trimmed)
            if detected:
                current_section = detected
                continue

            sections[current_section].append(trimmed)

        return {k: "\n".join(v) for k, v in sections.items() if v}


section_segmenter = SectionSegmenter()
