import re
from datetime import datetime
from typing import List, Dict, Any, Tuple


class ExperienceExtractor:
    DATE_RANGE_PATTERN = re.compile(
        r"(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,.]+)?\s*(\b20\d{2}|\b19\d{2})\s*(?:-|–|—|to)\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,.]+)?\s*(\b20\d{2}|\b19\d{2}|present|current)\b",
        re.IGNORECASE
    )

    MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    ROLE_KEYWORDS = [
        "engineer", "developer", "architect", "scientist", "manager", "lead",
        "intern", "consultant", "analyst", "specialist", "administrator", "director"
    ]

    @classmethod
    def extract(cls, experience_text: str, fallback_text: str = "") -> Tuple[List[Dict[str, Any]], float]:
        text = experience_text if experience_text.strip() else fallback_text
        if not text:
            return [], 0.0

        experiences = []
        total_months = 0

        lines = text.split("\n")
        current_entry = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            date_match = cls.DATE_RANGE_PATTERN.search(line_str)
            if date_match:
                if current_entry:
                    experiences.append(current_entry)

                start_str, end_str, months, is_curr = cls._parse_dates(date_match)
                total_months += months

                title, company = cls._extract_title_and_company(line_str)

                current_entry = {
                    "job_title": title or "Software Engineer",
                    "company": company or "Technology Company",
                    "location": None,
                    "start_date": start_str,
                    "end_date": end_str,
                    "is_current": is_curr,
                    "duration_months": months,
                    "description": "",
                    "key_achievements": []
                }
            elif current_entry:
                if line_str.startswith(("*", "-", "•", ">")) or len(line_str) > 25:
                    clean_bullet = re.sub(r"^[*•\->\s]+", "", line_str).strip()
                    current_entry["key_achievements"].append(clean_bullet)
                elif not current_entry["job_title"] or current_entry["job_title"] == "Software Engineer":
                    possible_title, possible_comp = cls._extract_title_and_company(line_str)
                    if possible_title:
                        current_entry["job_title"] = possible_title
                    if possible_comp:
                        current_entry["company"] = possible_comp

        if current_entry:
            experiences.append(current_entry)

        for exp in experiences:
            exp["description"] = "\n".join(exp["key_achievements"])

        total_years = round(total_months / 12.0, 1)
        return experiences, total_years

    @classmethod
    def _parse_dates(cls, match) -> Tuple[str, str, int, bool]:
        s_month_str, s_year_str, e_month_str, e_year_str = match.groups()

        start_year = int(s_year_str)
        start_month = cls.MONTH_MAP.get(s_month_str.lower()[:3], 1) if s_month_str else 1
        start_formatted = f"{start_year}-{start_month:02d}"

        is_current = False
        if not e_year_str or e_year_str.lower() in ("present", "current"):
            is_current = True
            now = datetime.now()
            end_year = now.year
            end_month = now.month
            end_formatted = "Present"
        else:
            end_year = int(e_year_str)
            end_month = cls.MONTH_MAP.get(e_month_str.lower()[:3], 12) if e_month_str else 12
            end_formatted = f"{end_year}-{end_month:02d}"

        months = max(1, (end_year - start_year) * 12 + (end_month - start_month))
        return start_formatted, end_formatted, months, is_current

    @classmethod
    def _extract_title_and_company(cls, line: str) -> Tuple[str, str]:
        clean = cls.DATE_RANGE_PATTERN.sub("", line).strip()
        parts = [p.strip() for p in re.split(r"[,|–—\-\@]", clean) if p.strip()]

        title = ""
        company = ""

        for part in parts:
            part_lower = part.lower()
            if any(rk in part_lower for rk in cls.ROLE_KEYWORDS):
                title = part
            elif not company and len(part) > 2:
                company = part

        return title, company


experience_extractor = ExperienceExtractor()
