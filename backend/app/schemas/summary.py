"""Response schema for PDF study summaries."""

from pydantic import BaseModel


class PdfSummaryResponse(BaseModel):
    filename: str
    summary: str
