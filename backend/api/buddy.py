from fastapi import APIRouter
from backend.services.virtual_gym_buddy import gym_buddy_response
from backend.services.llm_chat import llm_chat

router = APIRouter()

@router.get("/")
def buddy(message: str):
    return {"response": gym_buddy_response(message)}

@router.get("/llm")
def buddy_llm(message: str):
    return {"response": llm_chat(message)}
