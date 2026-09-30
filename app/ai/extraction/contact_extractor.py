import re
from typing import Dict, Optional


class ContactExtractor:
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        re.IGNORECASE
    )
    
    # Clean, robust phone number pattern matching domestic and international formats
    PHONE_PATTERN = re.compile(
        r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)?\d{3}\s*(?:[.-]\s*)?\d{4}"
    )

    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?",
        re.IGNORECASE
    )

    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?",
        re.IGNORECASE
    )

    @classmethod
    def extract(cls, raw_text: str, header_section: str = "") -> Dict[str, Optional[str]]:
        search_target = f"{header_section}\n{raw_text[:1500]}"

        email_match = cls.EMAIL_PATTERN.search(search_target)
        email = email_match.group(0).strip() if email_match else None

        phone_match = cls.PHONE_PATTERN.search(search_target)
        phone = phone_match.group(0).strip() if phone_match else None

        li_match = cls.LINKEDIN_PATTERN.search(raw_text)
        linkedin = li_match.group(0).strip() if li_match else None

        gh_match = cls.GITHUB_PATTERN.search(raw_text)
        github = gh_match.group(0).strip() if gh_match else None

        name = cls._extract_name(header_section or raw_text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github
        }

    @classmethod
    def _extract_name(cls, header_text: str) -> Optional[str]:
        lines = [line.strip() for line in header_text.split("\n") if line.strip()]
        for line in lines[:5]:
            if "@" in line or "http" in line or any(char.isdigit() for char in line):
                continue
            words = line.split()
            if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
                return line.title()
        return None


contact_extractor = ContactExtractor()
