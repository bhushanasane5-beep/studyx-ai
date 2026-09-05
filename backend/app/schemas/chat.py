"""Request and response schemas for the StudyX AI chat API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4_000)


class ChatResponse(BaseModel):
    response: str
