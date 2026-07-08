"""
Extracts raw text from an uploaded PDF resume.
Tries pdfplumber first (better layout handling), falls back to PyPDF2.
"""
import io
import pdfplumber

try:
    from PyPDF2 import PdfReader
except ImportError:  # pypdf is the maintained successor package
    from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes. Returns empty string on total failure."""
    text = _extract_with_pdfplumber(file_bytes)
    if text.strip():
        return text

    return _extract_with_pypdf2(file_bytes)


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    try:
        text_chunks = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
        return "\n".join(text_chunks)
    except Exception:
        return ""


def _extract_with_pypdf2(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_chunks = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text_chunks)
    except Exception:
        return ""


def get_page_count(file_bytes: bytes) -> int:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0
