"""StudyX AI backend application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.summaries import router as summaries_router

app = FastAPI(title="StudyX AI API")

app.add_middleware(
    CORSMiddleware,
  allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router)
app.include_router(summaries_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
