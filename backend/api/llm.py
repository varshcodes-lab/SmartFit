from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from backend.services.llm_chat import llm_chat
from backend.schemas.chat import ChatResponse

router = APIRouter(tags=["AI Coach"])

class ChatResponse(BaseModel):
    reply: str = Field(..., example="Keep going! You're doing great 💪")

@router.get("/", response_model=ChatResponse)
def chat(message: str):
    return llm_chat(message)

def chat(
    message: str = Query(..., description="User message")
):
    return llm_chat(message)
