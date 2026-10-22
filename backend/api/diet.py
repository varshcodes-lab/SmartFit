from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from services.diet_engine import build_diet_plan

diet_router=APIRouter(prefix="/recommendations",tags=["diet"])
class DietRequest(BaseModel):
 age:int=Field(ge=18,le=100)
 sex:Literal['male','female','unspecified']='unspecified'
 height_cm:float=Field(gt=120,le=230)
 weight_kg:float=Field(gt=30,le=350)
 activity_level:Literal['sedentary','light','moderate','very_active','extra_active']='moderate'
 goal:Literal['muscle_gain','strength','general_fitness','weight_loss']='general_fitness'
 dietary_preference:Literal['vegetarian','non-vegetarian','vegan']='vegetarian'
 allergies:list[str]=Field(default_factory=list,max_length=30)
 @field_validator('allergies')
 @classmethod
 def clean_allergies(cls,values):
  values=[x.strip().lower() for x in values if x and x.strip()]
  if any(len(x)>80 for x in values): raise ValueError('Each allergy entry must be 80 characters or fewer.')
  return values
@diet_router.post('/diet')
def generate_diet(request:DietRequest):
 try: return build_diet_plan(request.model_dump())
 except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
