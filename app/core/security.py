import os
import re
from pathlib import Path
from typing import Tuple
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

    return True, "File is valid and safe."


def anonymize_text(text: str) -> str:
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED EMAIL]", text)
    text = re.sub(r"(\+?[0-9]{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)(\d{3}[-.\s]?\d{4})", "[REDACTED PHONE]", text)
    return text
