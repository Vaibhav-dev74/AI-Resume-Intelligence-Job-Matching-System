import io
import os
import re
import zipfile
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from app.core.config import settings

MAGIC_BYTES = {
    "pdf": b"%PDF",
    "docx": b"PK\x03\x04"
}


def sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return clean


def validate_file_safety(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    if not file_bytes or len(file_bytes) == 0:
        return False, "File is empty."

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return False, f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."

    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"File extension '{ext}' is not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"

    if ext == ".pdf":
        if not file_bytes.startswith(MAGIC_BYTES["pdf"]):
            return False, "File signature does not match valid PDF specification."
    elif ext == ".docx":
        if not file_bytes.startswith(MAGIC_BYTES["docx"]):
            return False, "File signature does not match valid DOCX specification."

        # Guard against decompression zip bomb attacks
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                total_uncompressed = sum(info.file_size for info in z.infolist())
                if total_uncompressed > 50 * 1024 * 1024:  # 50MB uncompressed limit
                    return False, "DOCX file exceeds safe decompression ratio (potential zip bomb)."
        except Exception as e:
            return False, f"Malformed or corrupted DOCX archive: {e}"

    return True, "File is valid and safe."


def anonymize_text(text: str, candidate_name: Optional[str] = None) -> str:
    if not text:
        return ""

    # Redact Emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED EMAIL]", text)
    # Redact Phone Numbers
    text = re.sub(r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)?\d{3}\s*(?:[.-]\s*)?\d{4}", "[REDACTED PHONE]", text)
    # Redact Profile URLs (LinkedIn, GitHub)
    text = re.sub(r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in|github\.com)/[a-zA-Z0-9_-]+/?", "[REDACTED URL]", text, flags=re.IGNORECASE)

    # Redact Candidate Name if specified
    if candidate_name and candidate_name.strip() and candidate_name.lower() not in ("candidate", "unknown"):
        name_tokens = candidate_name.strip().split()
        if len(name_tokens) >= 2:
            full_pattern = rf"\b{re.escape(candidate_name.strip())}\b"
            text = re.sub(full_pattern, "[REDACTED CANDIDATE NAME]", text, flags=re.IGNORECASE)
            # Also redact first name if > 3 chars
            if len(name_tokens[0]) > 3:
                text = re.sub(rf"\b{re.escape(name_tokens[0])}\b", "[REDACTED NAME]", text, flags=re.IGNORECASE)

    return text


def anonymize_profile(profile_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a blind-screening anonymized copy of the candidate profile
    for unconscious bias reduction and compliance.
    """
    anonymized = dict(profile_dict)
    name = profile_dict.get("full_name", "")
    anonymized["full_name"] = "Candidate [Blind Screening]"
    anonymized["email"] = "[REDACTED]"
    anonymized["phone"] = "[REDACTED]"
    anonymized["linkedin_url"] = None
    anonymized["github_url"] = None
    anonymized["portfolio_url"] = None

    if anonymized.get("summary"):
        anonymized["summary"] = anonymize_text(anonymized["summary"], candidate_name=name)

    return anonymized
