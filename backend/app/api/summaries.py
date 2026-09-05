"""PDF summary endpoint for the StudyX AI MVP."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.summary import PdfSummaryResponse
from app.services.ai_service import AIServiceError, ai_service
from app.services.document_service import (
    MAX_PDF_SIZE_BYTES,
    DocumentProcessingError,
    extract_pdf_text,
    validate_pdf,
)

router = APIRouter(prefix="/api/summaries", tags=["summaries"])


@router.post("/pdf", response_model=PdfSummaryResponse)
async def summarize_pdf(file: UploadFile = File(...)) -> PdfSummaryResponse:
    """Extract PDF text and generate study-ready notes."""
    content = await file.read(MAX_PDF_SIZE_BYTES + 1)
    try:
        validate_pdf(file.filename, file.content_type, content)
        extracted_text = extract_pdf_text(content)
        summary = await ai_service.summarize(extracted_text)
    except DocumentProcessingError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    except AIServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    finally:
        await file.close()

    return PdfSummaryResponse(filename=file.filename or "study-notes.pdf", summary=summary)
