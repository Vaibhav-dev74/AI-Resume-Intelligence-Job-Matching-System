import io
from typing import Tuple
from app.core.logging import logger


class PDFParser:
    MIN_CHAR_DENSITY_PER_PAGE = 40

    @classmethod
    def extract_text(cls, file_bytes: bytes) -> Tuple[str, int]:
        try:
            import fitz
        except ImportError:
            raise RuntimeError("PyMuPDF is not installed. Please install 'pymupdf'.")

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Failed to open PDF document: {e}")

        if doc.is_encrypted:
            raise ValueError("The PDF document is password-protected or encrypted.")

        extracted_pages = []
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()

            if len(text) < cls.MIN_CHAR_DENSITY_PER_PAGE:
                logger.info(f"Page {page_num + 1} has low text density ({len(text)} chars). Attempting OCR fallback.")
                ocr_text = cls._ocr_fallback(page)
                if ocr_text:
                    text = ocr_text

            extracted_pages.append(text)

        doc.close()
        full_text = "\n\n".join(extracted_pages)
        return full_text.strip(), total_pages

    @classmethod
    def _ocr_fallback(cls, page) -> str:
        try:
            import pytesseract
            from PIL import Image

            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR fallback failed: {e}")
            return ""


pdf_parser = PDFParser()
