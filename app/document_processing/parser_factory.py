from pathlib import Path
from typing import Dict, Tuple
from app.document_processing.pdf_parser import pdf_parser
from app.document_processing.docx_parser import docx_parser
from app.document_processing.sanitizer import text_sanitizer
from app.document_processing.section_segmenter import section_segmenter


class DocumentParserFactory:
    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, str], int]:
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            raw_text, pages = pdf_parser.extract_text(file_bytes)
        elif ext == ".docx":
            raw_text, pages = docx_parser.extract_text(file_bytes)
        elif ext == ".txt":
            raw_text = file_bytes.decode("utf-8", errors="replace")
            pages = 1
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        cleaned_text = text_sanitizer.clean(raw_text)
        if not cleaned_text:
            raise ValueError("The uploaded document contains no extractable text.")

        sections = section_segmenter.segment(cleaned_text)
        return cleaned_text, sections, pages


document_parser_factory = DocumentParserFactory()
