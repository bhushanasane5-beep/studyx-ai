"""Safe extraction of text-based PDF documents."""

from __future__ import annotations

import fitz
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024
MAX_SUMMARY_CHARACTERS = 30_000


class DocumentProcessingError(Exception):
    """A safe failure while validating or extracting a PDF."""


def validate_pdf(filename: str | None, content_type: str | None, content: bytes) -> None:
    """Reject unsupported, oversized, or non-PDF uploads."""
    if not filename or not filename.lower().endswith(".pdf"):
        raise DocumentProcessingError("Please upload a PDF file.")
    if content_type and content_type not in {"application/pdf", "application/x-pdf"}:
        raise DocumentProcessingError("Please upload a valid PDF file.")
    if not content:
        raise DocumentProcessingError("The uploaded PDF is empty.")
    if len(content) > MAX_PDF_SIZE_BYTES:
        raise DocumentProcessingError("PDF files must be 10 MB or smaller.")
    if not content.startswith(b"%PDF-"):
        raise DocumentProcessingError("Please upload a valid PDF file.")


def extract_pdf_text(content: bytes) -> str:
    """Extract readable text and limit the AI input to a practical size."""
    try:
        document = PdfReader(BytesIO(content), strict=False)
        text = "\n\n".join(page.extract_text() or "" for page in document.pages)
    except (PdfReadError, OSError, RuntimeError, ValueError) as error:
        raise DocumentProcessingError("We could not read that PDF. Please try another file.") from error

    normalized_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not normalized_text:
        raise DocumentProcessingError(
            "No selectable text was found in this PDF. Scanned PDFs are not supported yet."
        )
    return normalized_text[:MAX_SUMMARY_CHARACTERS]
