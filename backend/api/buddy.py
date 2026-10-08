from fastapi import APIRouter
from services.virtual_gym_buddy import gym_buddy_response
from services.llm_chat import llm_chat

router = APIRouter()

@router.get("/")
def buddy(message: str):
    return {"response": gym_buddy_response(message)}

@router.get("/llm")
def buddy_llm(message: str):
    return {"response": llm_chat(message)}
