"""Chat endpoint for the initial StudyX AI experience."""

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIServiceError, ai_service
from app.services.pdf_service import extract_text_from_pdf




router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def create_chat_reply(payload: ChatRequest) -> ChatResponse:
    """Generate one assistant reply for a student message."""
    try:
        reply = await ai_service.chat(payload.message.strip())
    except AIServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    return ChatResponse(response=reply)
@router.post("/pdf-summary")
async def create_pdf_summary(file: UploadFile = File(...)):
    """Extract text from a PDF and generate an AI study summary."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a PDF file.",
        )

    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF is empty.",
            )

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        document_text = extract_text_from_pdf(temp_path)

        if not document_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from this PDF.",
            )

        summary = await ai_service.summarize(document_text)

        return {"summary": summary}

    except AIServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
